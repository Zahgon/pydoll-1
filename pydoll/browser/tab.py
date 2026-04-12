from __future__ import annotations

import asyncio
import base64 as _b64
import contextlib
import io
import logging
import shutil
import warnings
import zipfile
from contextlib import asynccontextmanager
from functools import partial
from pathlib import Path
from tempfile import mkdtemp
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Optional,
    TypeAlias,
    TypeVar,
    Union,
    cast,
    overload,
)

import aiofiles

from pydoll.browser.requests import Request
from pydoll.commands import (
    DomCommands,
    FetchCommands,
    NetworkCommands,
    PageCommands,
    RuntimeCommands,
    StorageCommands,
    TargetCommands,
)
from pydoll.connection import ConnectionHandler
from pydoll.constants import By, PageLoadState
from pydoll.elements.mixins import FindElementsMixin
from pydoll.elements.shadow_root import ShadowRoot
from pydoll.elements.web_element import WebElement
from pydoll.exceptions import (
    CommandExecutionTimeout,
    DownloadTimeout,
    IFrameNotFound,
    InvalidFileExtension,
    InvalidIFrame,
    InvalidScriptWithElement,
    InvalidTabInitialization,
    MissingScreenshotPath,
    NavigationError,
    NetworkEventsNotEnabled,
    NoDialogPresent,
    NotAnIFrame,
    PageLoadTimeout,
    TopLevelTargetRequired,
    WaitElementTimeout,
    WebSocketConnectionClosed,
)
from pydoll.extractor.engine import ExtractionEngine
from pydoll.interactions import KeyboardAPI, MouseAPI, ScrollAPI
from pydoll.interactions.iframe import IFrameContext
from pydoll.protocol.browser.types import DownloadBehavior, DownloadProgressState
from pydoll.protocol.dom.types import Node, ShadowRootType
from pydoll.protocol.network.types import ResourceType
from pydoll.protocol.page.events import PageEvent
from pydoll.protocol.page.types import FrameResourceTree, ScreenshotFormat
from pydoll.protocol.runtime.methods import (
    CallFunctionOnResponse,
    EvaluateResponse,
    SerializationOptions,
)
from pydoll.protocol.runtime.types import CallArgument
from pydoll.protocol.target.types import TargetInfo
from pydoll.utils import (
    decode_base64_to_bytes,
    has_return_outside_function,
)
from pydoll.utils.bundle import (
    build_asset_filename,
    collect_frame_resources,
    filter_fetchable_resources,
    inline_all_assets,
    rewrite_html_urls,
)

if TYPE_CHECKING:
    from pydoll.browser.chromium.base import Browser
    from pydoll.extractor.model import ExtractionModel
    from pydoll.protocol.base import EmptyResponse, Response
    from pydoll.protocol.browser.events import (
        DownloadProgressEvent,
        DownloadWillBeginEvent,
    )
    from pydoll.protocol.dom.methods import (
        DescribeNodeResponse,
        GetDocumentResponse,
        ResolveNodeResponse,
    )
    from pydoll.protocol.fetch.types import AuthChallengeResponseType, HeaderEntry, RequestStage
    from pydoll.protocol.network.events import RequestWillBeSentEvent
    from pydoll.protocol.network.methods import GetCookiesResponse as NetworkGetCookiesResponse
    from pydoll.protocol.network.methods import GetResponseBodyResponse
    from pydoll.protocol.network.types import (
        Cookie,
        CookieParam,
        ErrorReason,
        RequestMethod,
    )
    from pydoll.protocol.page.events import FileChooserOpenedEvent
    from pydoll.protocol.page.methods import (
        CaptureScreenshotResponse,
        GetResourceContentResponse,
        GetResourceTreeResponse,
        NavigateResponse,
        PrintToPDFResponse,
    )
    from pydoll.protocol.runtime.methods import CallFunctionOnResponse, EvaluateResponse
    from pydoll.protocol.storage.methods import GetCookiesResponse as StorageGetCookiesResponse
    from pydoll.protocol.target.methods import AttachToTargetResponse, GetTargetsResponse

logger = logging.getLogger(__name__)

IFrame: TypeAlias = 'Tab'

T = TypeVar('T', bound='ExtractionModel')

_CLOUDFLARE_CHALLENGE_DOMAIN = 'challenges.cloudflare.com'
_CLOUDFLARE_IFRAME_SELECTOR = f'iframe[src*="{_CLOUDFLARE_CHALLENGE_DOMAIN}"]'
_CLOUDFLARE_CHECKBOX_SELECTOR = 'span.cb-i'


class Tab(FindElementsMixin):
    """
    Controls a browser tab via Chrome DevTools Protocol.

    Primary interface for web page automation including navigation, DOM manipulation,
    JavaScript execution, event handling, network monitoring, and specialized tasks
    like Cloudflare bypass.
    """

    def __init__(
        self,
        browser: Browser,
        connection_port: Optional[int] = None,
        target_id: Optional[str] = None,
        browser_context_id: Optional[str] = None,
        ws_address: Optional[str] = None,
    ):
        """
        Initialize tab controller for existing browser tab.

        Args:
            browser: Browser instance that created this tab.
            connection_port: CDP WebSocket port.
            target_id: CDP target identifier for this tab.
            browser_context_id: Optional browser context ID.
            ws_address: Optional WebSocket address for this tab.
        """
        if not any([connection_port, target_id, ws_address]):
            raise InvalidTabInitialization()

        self._browser = browser
        self._connection_port = connection_port
        self._target_id = target_id
        self._ws_address = ws_address
        self._browser_context_id = browser_context_id
        self._connection_handler = self._get_connection_handler()
        self._page_events_enabled = False
        self._network_events_enabled = False
        self._fetch_events_enabled = False
        self._dom_events_enabled = False
        self._runtime_events_enabled = False
        self._intercept_file_chooser_dialog_enabled = False
        self._cloudflare_captcha_callback_id: Optional[int] = None
        self._request: Optional[Request] = None
        self._scroll: Optional[ScrollAPI] = None
        self._keyboard: Optional[KeyboardAPI] = None
        self._mouse: MouseAPI = MouseAPI(self)
        self._extraction_engine: Optional[ExtractionEngine] = None
        logger.debug(
            (
                f'Tab initialized: target_id={self._target_id}, '
                f'ws_address_set={bool(self._ws_address)}, '
                f'context_id={self._browser_context_id}, port={self._connection_port}'
            )
        )

    @property
    def page_events_enabled(self) -> bool:
        """Whether CDP Page domain events are enabled."""
        pass

    @property
    def network_events_enabled(self) -> bool:
        """Whether CDP Network domain events are enabled."""
        pass

    @property
    def fetch_events_enabled(self) -> bool:
        """Whether CDP Fetch domain events (request interception) are enabled."""
        pass

    @property
    def dom_events_enabled(self) -> bool:
        """Whether CDP DOM domain events are enabled."""
        pass

    @property
    def runtime_events_enabled(self) -> bool:
        """Whether CDP Runtime domain events are enabled."""
        pass

    @property
    def request(self) -> Request:
        """
        Get the request object for making HTTP requests using the browser's fetch API.

        Returns:
            Request: An instance of the Request class for making HTTP requests.
        """
        if self._request is None:
            self._request = Request(self)
        return self._request

    @property
    def scroll(self) -> ScrollAPI:
        """
        Get the scroll API for controlling page scroll behavior.

        Returns:
            ScrollAPI: An instance of the ScrollAPI class for scroll operations.
        """
        pass

    @property
    def keyboard(self) -> KeyboardAPI:
        """
        Get the keyboard API for controlling keyboard input at page level.

        Returns:
            KeyboardAPI: An instance of the KeyboardAPI class for keyboard operations.
        """
        pass

    @property
    def mouse(self) -> MouseAPI:
        """
        Get the mouse API for controlling mouse input.

        Returns:
            MouseAPI: An instance of the MouseAPI class for mouse operations.
        """
        pass

    @property
    def _extractor(self) -> ExtractionEngine:
        """Lazy-initialized extraction engine."""
        pass

    async def extract(
        self,
        model: type[T],
        *,
        scope: Optional[str] = None,
        timeout: int = 0,
    ) -> T:
        """Extract structured data from the page into a typed model.

        Args:
            model: ExtractionModel subclass defining the extraction schema.
            scope: Optional CSS/XPath selector to limit extraction region.
            timeout: Seconds to wait for elements (0 = no wait).

        Returns:
            Populated model instance with extracted data.

        Raises:
            FieldExtractionFailed: If a required field cannot be extracted.
            InvalidExtractionModel: If model definition is invalid.
        """
        pass

    async def extract_all(
        self,
        model: type[T],
        *,
        scope: str,
        timeout: int = 0,
        limit: Optional[int] = None,
    ) -> list[T]:
        """Extract multiple items from repeated containers on the page.

        Each element matching the scope selector generates one model instance.
        Fields are resolved relative to each scope container.

        Args:
            model: ExtractionModel subclass defining the extraction schema.
            scope: CSS/XPath selector for the repeated container (required).
            timeout: Seconds to wait for elements (0 = no wait).
            limit: Maximum number of items to extract (None = all).

        Returns:
            List of populated model instances.
        """
        pass

    @property
    def intercept_file_chooser_dialog_enabled(self) -> bool:
        """Whether file chooser dialog interception is active."""
        pass

    @property
    async def current_url(self) -> str:
        """Get current page URL (reflects redirects and client-side navigation)."""
        pass

    @property
    async def page_source(self) -> str:
        """Get complete HTML source of current page (live DOM state)."""
        pass

    @property
    async def title(self) -> str:
        """Get current page title."""
        pass

    async def enable_page_events(self):
        """Enable CDP Page domain events (load, navigation, dialogs, etc.)."""
        pass

    async def enable_network_events(self):
        """Enable CDP Network domain events (requests, responses, etc.)."""
        logger.debug('Enabling Network events')
        response = await self._execute_command(NetworkCommands.enable())
        self._network_events_enabled = True
        logger.debug('Network events enabled')
        return response

    async def enable_fetch_events(
        self,
        handle_auth: bool = False,
        resource_type: Optional[ResourceType] = None,
        request_stage: Optional[RequestStage] = None,
    ):
        """
        Enable CDP Fetch domain for request interception.

        Args:
            handle_auth: Intercept authentication challenges.
            resource_type: Filter by resource type (all if None).
            request_stage: When to intercept (Request/Response).

        Note:
            Intercepted requests must be explicitly continued or timeout.
        """
        logger.debug(
            f'Enabling Fetch events: handle_auth={handle_auth}, resource_type={resource_type}, '
            f'stage={request_stage}'
        )
        response: Response[EmptyResponse] = await self._execute_command(
            FetchCommands.enable(
                handle_auth_requests=handle_auth,
                resource_type=resource_type,
                request_stage=request_stage,
            )
        )
        self._fetch_events_enabled = True
        logger.debug('Fetch events enabled')
        return response

    async def enable_dom_events(self):
        """Enable CDP DOM domain events (document structure changes)."""
        pass

    async def enable_runtime_events(self):
        """Enable CDP Runtime domain events."""
        pass

    async def enable_intercept_file_chooser_dialog(self):
        """
        Enable file chooser dialog interception for automated uploads.

        Note:
            Use expect_file_chooser context manager for convenience.
        """
        pass

    async def enable_auto_solve_cloudflare_captcha(
        self,
        custom_selector: Optional[tuple[By, str]] = None,
        time_before_click: Optional[float] = None,
        time_to_wait_captcha: float = 5,
    ):
        """
        Enable automatic Cloudflare Turnstile captcha bypass.

        Args:
            custom_selector: Deprecated — ignored. Cloudflare Turnstile is now
                detected automatically via shadow root inspection.
            time_before_click: Deprecated — ignored. The checkbox is now
                located via shadow root polling and clicked immediately.
            time_to_wait_captcha: Timeout for captcha detection (default 5s).
        """
        pass

    async def disable_fetch_events(self):
        """Disable CDP Fetch domain and release paused requests."""
        pass

    async def disable_page_events(self):
        """Disable CDP Page domain events."""
        pass

    async def disable_network_events(self):
        """Disable CDP Network domain events."""
        logger.debug('Disabling Network events')
        response = await self._execute_command(NetworkCommands.disable())
        self._network_events_enabled = False
        logger.debug('Network events disabled')
        return response

    async def disable_dom_events(self):
        """Disable CDP DOM domain events."""
        pass

    async def disable_runtime_events(self):
        """Disable CDP Runtime domain events."""
        pass

    async def disable_intercept_file_chooser_dialog(self):
        """Disable file chooser dialog interception."""
        pass

    async def disable_auto_solve_cloudflare_captcha(self):
        """Disable automatic Cloudflare Turnstile captcha bypass."""
        pass

    async def close(self):
        """
        Close this browser tab.

        Note:
            Tab instance becomes invalid after calling this method.
        """
        logger.info(f'Closing tab: target_id={self._target_id}')
        result = await self._execute_command(PageCommands.close())
        self._browser._tabs_opened.pop(self._target_id)
        logger.debug('Tab closed and removed from browser registry')
        return result

    async def get_frame(self, frame: 'WebElement') -> IFrame:
        """
        .. deprecated:: ?.?.?
            Use iframe `WebElement` instances directly; this method will be removed in
            a future version.

        Get Tab object for interacting with iframe content.

        Args:
            frame: Tab representing the iframe tag.

        Returns:
            Tab instance configured for iframe interaction.

        Raises:
            NotAnIFrame: If element is not an iframe.
            InvalidIFrame: If iframe lacks valid src attribute.
            IFrameNotFound: If iframe target not found in browser.
        """
        pass

    async def find_shadow_roots(self, deep: bool = False, timeout: float = 0) -> list[ShadowRoot]:
        """
        Find all shadow roots in the page.

        Traverses the entire DOM tree (including iframes and nested shadow DOMs)
        to collect all shadow roots found. This is especially useful when the
        shadow host element selector is unknown or dynamic (e.g., Cloudflare
        challenge pages).

        Args:
            deep: If True, also traverses cross-origin iframes (OOPIFs) to
                discover shadow roots inside them. The returned ShadowRoot
                objects will automatically route CDP commands through the
                correct OOPIF session.
            timeout: Maximum seconds to wait for shadow roots to appear.
                When > 0, repeatedly polls the DOM (every 0.5s) until at least
                one shadow root is found or the timeout expires. Useful when
                shadow hosts are injected asynchronously (e.g., Cloudflare
                Turnstile loading inside an OOPIF).

        Returns:
            List of ShadowRoot instances found in the page.

        Raises:
            WaitElementTimeout: If timeout > 0 and no shadow roots are found
                within the specified duration.
        """
        pass

    async def _collect_all_shadow_roots(self, deep: bool) -> list[ShadowRoot]:
        """Collect shadow roots from the main document and optionally OOPIFs."""
        pass

    async def _resolve_shadow_host(self, host_backend_id: int | None) -> WebElement | None:
        """Resolve the host element for a shadow root (best-effort)."""
        pass

    async def _collect_oopif_shadow_roots(self) -> list[ShadowRoot]:
        """Discover shadow roots inside cross-origin iframes (OOPIFs)."""
        pass

    async def _collect_shadow_roots_from_oopif_target(
        self,
        target: TargetInfo,
        browser_handler: ConnectionHandler,
    ) -> list[ShadowRoot]:
        """Collect shadow roots from a single OOPIF target."""
        pass

    async def _resolve_oopif_shadow_entry(
        self,
        shadow_data: Node,
        host_backend_id: int | None,
        browser_handler: ConnectionHandler,
        session_id: str,
        iframe_context: IFrameContext,
    ) -> ShadowRoot | None:
        """Resolve a single shadow root entry from an OOPIF."""
        pass

    async def _resolve_oopif_shadow_host(
        self,
        host_backend_id: int | None,
        browser_handler: ConnectionHandler,
        session_id: str,
    ) -> WebElement | None:
        """Resolve the host element for a shadow root inside an OOPIF (best-effort)."""
        pass

    @staticmethod
    def _collect_shadow_roots_from_tree(node: Node, results: list[tuple[Node, int | None]]) -> None:
        """Recursively walk a DOM tree collecting shadow root entries."""
        pass

    async def bring_to_front(self):
        """Brings the page to front."""
        pass

    async def get_cookies(self) -> list[Cookie]:
        """Get all cookies accessible from current page."""
        pass

    async def get_network_response_body(self, request_id: str) -> str:
        """
        Get the response body for a given request ID.

        Args:
            request_id: Request ID to get the response body for.

        Returns:
            The response body for the given request ID.

        Raises:
            NetworkEventsNotEnabled: If network events are not enabled.
        """
        pass

    async def get_network_logs(self, filter: Optional[str] = None) -> list[RequestWillBeSentEvent]:
        """
        Get network logs.

        Args:
            filter: Filter to apply to the network logs.

        Returns:
            The network logs.

        Raises:
            NetworkEventsNotEnabled: If network events are not enabled.
        """
        pass

    async def set_cookies(self, cookies: list[CookieParam]):
        """
        Set multiple cookies for current page.

        Args:
            cookies: Cookie parameters (name/value required, others optional).

        Note:
            Defaults to current page's domain if not specified.
        """
        pass

    async def delete_all_cookies(self):
        """Delete all cookies from current browser context."""
        pass

    async def go_to(self, url: str, timeout: int = 300):
        """
        Navigate to URL and wait for loading to complete.

        Args:
            url: Target URL to navigate to.
            timeout: Maximum seconds to wait for page load (default 300).

        Raises:
            NavigationError: If the navigation fails (e.g., DNS error).
            PageLoadTimeout: If page doesn't finish loading within timeout.
        """
        pass

    async def refresh(
        self,
        ignore_cache: bool = False,
        script_to_evaluate_on_load: Optional[str] = None,
    ):
        """
        Reload current page and wait for completion.

        Args:
            ignore_cache: Bypass browser cache if True.
            script_to_evaluate_on_load: JavaScript to execute after load.

        Raises:
            PageLoadTimeout: If page doesn't finish loading within timeout.
        """
        pass

    async def take_screenshot(
        self,
        path: Optional[str | Path] = None,
        quality: int = 100,
        beyond_viewport: bool = False,
        as_base64: bool = False,
    ) -> Optional[str]:
        """
        Capture screenshot of current page.

        Args:
            path: File path for screenshot (extension determines format).
            quality: Image quality 0-100 (default 100).
            beyond_viewport: The page will be scrolled to the bottom and the screenshot will
                include the entire page
            as_base64: Return as base64 string instead of saving file.

        Returns:
            Base64 screenshot data if as_base64=True, None otherwise.

        Raises:
            InvalidFileExtension: If file extension not supported.
            MissingScreenshotPath: If path is None and as_base64 is False.
        """
        pass

    async def print_to_pdf(
        self,
        path: Optional[str | Path] = None,
        landscape: bool = False,
        display_header_footer: bool = False,
        print_background: bool = True,
        scale: float = 1.0,
        as_base64: bool = False,
    ) -> Optional[str]:
        """
        Generate PDF of current page.

        Args:
            path: File path for PDF output. Required if as_base64=False.
            landscape: Use landscape orientation.
            display_header_footer: Include header/footer.
            print_background: Include background graphics.
            scale: Scale factor (0.1-2.0).
            as_base64: Return as base64 string instead of saving.

        Returns:
            Base64 PDF data if as_base64=True, None otherwise.

        Raises:
            ValueError: If path is not provided when as_base64=False.
        """
        pass

    async def save_bundle(self, path: str | Path, inline_assets: bool = False) -> None:
        """
        Save current page and its assets as a .zip bundle for offline viewing.

        Captures the page HTML along with CSS, JS, images, fonts, and media
        into a single zip archive. The archive contains an ``index.html`` with
        URLs rewritten to reference local asset files.

        Args:
            path: Destination path for the ``.zip`` file.
            inline_assets: When True, embed all assets directly into
                ``index.html`` using data URIs, ``<style>``, and ``<script>``
                tags instead of saving them as separate files.

        Raises:
            InvalidFileExtension: If path does not end with ``.zip``.
        """
        pass

    async def _fetch_document_html(self, frame_tree: FrameResourceTree) -> str:
        """Fetch the main document HTML from the frame tree."""
        pass

    async def _fetch_bundle_assets(
        self,
        frame_tree: FrameResourceTree,
        page_url: str,
    ) -> dict[str, tuple[str, bytes, str, ResourceType]]:
        """Fetch all bundleable resources and return an asset map."""
        pass

    async def has_dialog(self) -> bool:
        """
        Check if JavaScript dialog is currently displayed.

        Note:
            Page events must be enabled to detect dialogs.
        """
        pass

    async def get_dialog_message(self) -> str:
        """
        Get message text from current JavaScript dialog.

        Raises:
            NoDialogPresent: If no dialog is currently displayed.
        """
        pass

    async def handle_dialog(self, accept: bool, prompt_text: Optional[str] = None):
        """
        Respond to JavaScript dialog.

        Args:
            accept: Accept/confirm dialog if True, dismiss/cancel if False.
            prompt_text: Text for prompt dialogs (ignored for alert/confirm).

        Raises:
            NoDialogPresent: If no dialog is currently displayed.

        Note:
            Page events must be enabled to handle dialogs.
        """
        pass

    @overload
    async def execute_script(
        self,
        script: str,
        *,
        object_group: Optional[str] = None,
        include_command_line_api: Optional[bool] = None,
        silent: Optional[bool] = None,
        context_id: Optional[int] = None,
        return_by_value: Optional[bool] = None,
        generate_preview: Optional[bool] = None,
        user_gesture: Optional[bool] = None,
        await_promise: Optional[bool] = None,
        throw_on_side_effect: Optional[bool] = None,
        timeout: Optional[float] = None,
        disable_breaks: Optional[bool] = None,
        repl_mode: Optional[bool] = None,
        allow_unsafe_eval_blocked_by_csp: Optional[bool] = None,
        unique_context_id: Optional[str] = None,
        serialization_options: Optional[SerializationOptions] = None,
    ) -> EvaluateResponse: ...

    @overload
    async def execute_script(
        self,
        script: str,
        element: WebElement,
        *,
        arguments: Optional[list[CallArgument]] = None,
        silent: Optional[bool] = None,
        return_by_value: Optional[bool] = None,
        generate_preview: Optional[bool] = None,
        user_gesture: Optional[bool] = None,
        await_promise: Optional[bool] = None,
        execution_context_id: Optional[int] = None,
        object_group: Optional[str] = None,
        throw_on_side_effect: Optional[bool] = None,
        unique_context_id: Optional[str] = None,
        serialization_options: Optional[SerializationOptions] = None,
    ) -> CallFunctionOnResponse: ...

    async def execute_script(
        self,
        script: str,
        element: Optional[WebElement] = None,
        *,
        arguments: Optional[list[CallArgument]] = None,
        object_group: Optional[str] = None,
        include_command_line_api: Optional[bool] = None,
        silent: Optional[bool] = None,
        context_id: Optional[int] = None,
        return_by_value: Optional[bool] = None,
        generate_preview: Optional[bool] = None,
        user_gesture: Optional[bool] = None,
        await_promise: Optional[bool] = None,
        execution_context_id: Optional[int] = None,
        throw_on_side_effect: Optional[bool] = None,
        timeout: Optional[float] = None,
        disable_breaks: Optional[bool] = None,
        repl_mode: Optional[bool] = None,
        allow_unsafe_eval_blocked_by_csp: Optional[bool] = None,
        unique_context_id: Optional[str] = None,
        serialization_options: Optional[SerializationOptions] = None,
    ) -> Union[EvaluateResponse, CallFunctionOnResponse]:
        """
        Execute JavaScript in page context.

        Args:
            script (str): JavaScript code to execute.
            element (Optional[WebElement]): Optional WebElement to execute script on.
            arguments (Optional[list[CallArgument]]): Arguments to pass to the function.
            object_group (Optional[str]): Symbolic group name for the result (Runtime.evaluate).
            include_command_line_api (Optional[bool]): Whether to include command line API
                (Runtime.evaluate).
            silent (Optional[bool]): Whether to silence exceptions (Runtime.evaluate).
            context_id (Optional[int]): ID of the execution context to evaluate in
                (Runtime.evaluate).
            return_by_value (Optional[bool]): Whether to return the result by value instead of
                reference (Runtime.evaluate).
            generate_preview (Optional[bool]): Whether to generate a preview for the result
                (Runtime.evaluate).
            user_gesture (Optional[bool]): Whether to treat evaluation as initiated by user
                gesture (Runtime.evaluate).
            await_promise (Optional[bool]): Whether to await promise result (Runtime.evaluate).
            execution_context_id (Optional[int]): ID of the execution context to call the
                function in.
            throw_on_side_effect (Optional[bool]): Whether to throw if side effect cannot be
                ruled out (Runtime.evaluate).
            timeout (Optional[float]): Timeout in milliseconds (Runtime.evaluate).
            disable_breaks (Optional[bool]): Whether to disable breakpoints during evaluation
                (Runtime.evaluate).
            repl_mode (Optional[bool]): Whether to execute in REPL mode (Runtime.evaluate).
            allow_unsafe_eval_blocked_by_csp (Optional[bool]): Allow unsafe evaluation
                (Runtime.evaluate).
            unique_context_id (Optional[str]): Unique context ID for evaluation
                (Runtime.evaluate).
            serialization_options (Optional[SerializationOptions]): Serialization options for
                the result (Runtime.evaluate).

        Returns:
            Union[EvaluateResponse, CallFunctionOnResponse]: The result of the script execution.

        Raises:
            InvalidScriptWithElement: If script uses 'argument' keyword but no element is provided.

        Examples:
            # Execute a simple script to log a message
            await page.execute_script('console.log("Hello World")')

            # Execute a script that returns the page title
            await page.execute_script('return document.title')

            # Execute a script on an element to click it
            await page.execute_script('argument.click()', element)

            # Execute a script on an element to set its value
            await page.execute_script('argument.value = "Hello"', element)
        """
        logger.debug(f'Executing script: with_element={bool(element)}, length={len(script)}')
        if element is not None:
            warnings.warn(
                'Passing a WebElement to Tab.execute_script() is deprecated. '
                'Use WebElement.execute_script() instead.',
                DeprecationWarning,
                stacklevel=2,
            )

            return await element.execute_script(
                script,
                arguments=arguments,
                silent=silent,
                return_by_value=return_by_value,
                generate_preview=generate_preview,
                user_gesture=user_gesture,
                await_promise=await_promise,
                execution_context_id=execution_context_id,
                object_group=object_group,
                throw_on_side_effect=throw_on_side_effect,
                unique_context_id=unique_context_id,
                serialization_options=serialization_options,
            )

        if has_return_outside_function(script):
            script = f'(function(){{ {script} }})()'

        command = self._get_evaluate_command(
            script,
            object_group=object_group,
            include_command_line_api=include_command_line_api,
            silent=silent,
            context_id=context_id,
            return_by_value=return_by_value,
            generate_preview=generate_preview,
            user_gesture=user_gesture,
            await_promise=await_promise,
            throw_on_side_effect=throw_on_side_effect,
            timeout=timeout,
            disable_breaks=disable_breaks,
            repl_mode=repl_mode,
            allow_unsafe_eval_blocked_by_csp=allow_unsafe_eval_blocked_by_csp,
            unique_context_id=unique_context_id,
            serialization_options=serialization_options,
        )
        logger.debug(f'Executing script without element: length={len(script)}')
        result: Union[EvaluateResponse, CallFunctionOnResponse] = await self._execute_command(
            command
        )
        self._validate_argument_error(result)
        return result

    # TODO: think about how to remove these duplications with the base class
    async def continue_request(
        self,
        request_id: str,
        url: Optional[str] = None,
        method: Optional[RequestMethod] = None,
        post_data: Optional[str] = None,
        headers: Optional[list[HeaderEntry]] = None,
        intercept_response: Optional[bool] = None,
    ):
        """
        Continue paused request without modifications.
        """
        pass

    async def fail_request(self, request_id: str, error_reason: ErrorReason):
        """Fail request with error code."""
        pass

    async def fulfill_request(
        self,
        request_id: str,
        response_code: int,
        response_headers: Optional[list[HeaderEntry]] = None,
        body: Optional[str] = None,
        response_phrase: Optional[str] = None,
    ):
        """Fulfill request with response data."""
        pass

    async def continue_with_auth(
        self,
        request_id: str,
        auth_challenge_response: AuthChallengeResponseType,
        proxy_username: Optional[str] = None,
        proxy_password: Optional[str] = None,
    ):
        """Continue a paused request replying to an authentication challenge.

        Useful for proxy auth (407) or server auth (401) when Fetch is enabled
        with handle_auth=True.
        """
        pass

    @asynccontextmanager
    async def expect_file_chooser(
        self, files: str | Path | list[str | Path]
    ) -> AsyncGenerator[None, None]:
        """
        Context manager for automatic file upload handling.

        Args:
            files: File path(s) for upload.
        """
        pass

    @asynccontextmanager
    async def expect_and_bypass_cloudflare_captcha(
        self,
        custom_selector: Optional[tuple[By, str]] = None,
        time_before_click: Optional[float] = None,
        time_to_wait_captcha: float = 5,
    ) -> AsyncGenerator[None, None]:
        """
        Context manager for automatic Cloudflare captcha bypass.

        Args:
            custom_selector: Deprecated — ignored. Cloudflare Turnstile is now
                detected automatically via shadow root inspection.
            time_before_click: Deprecated — ignored. The checkbox is now
                located via shadow root polling and clicked immediately.
            time_to_wait_captcha: Timeout for captcha detection (default 5s).
        """
        pass

    @asynccontextmanager
    async def expect_download(
        self,
        keep_file_at: Optional[Union[str, Path]] = None,
        timeout: Optional[float] = None,
    ) -> AsyncGenerator[_DownloadHandle, None]:
        """
        Context manager for handling a file download triggered inside the block.

        Behavior:
        - If keep_file_at is provided, configure browser to save into that directory and keep file.
        - Otherwise, a temporary directory is used and cleaned up after the context.

        Args:
            keep_file_at: Directory to persist the file. If None, uses a temporary
                directory and cleans it up afterwards.
            timeout: Max seconds to wait for download completion. Defaults to 60.

        Yields:
            _DownloadHandle: Handle to read the downloaded file (bytes/base64) and check its path.
        """
        pass

    async def _cleanup_download_context(
        self,
        cb_id_progress: int,
        page_events_was_enabled: bool,
        cleanup_dir: bool,
        state: dict[str, Any],
        download_dir: str,
    ) -> None:
        pass

    @overload
    async def on(
        self, event_name: str, callback: Callable[[dict], Any], temporary: bool = False
    ) -> int: ...
    @overload
    async def on(
        self, event_name: str, callback: Callable[[dict], Awaitable[Any]], temporary: bool = False
    ) -> int: ...
    async def on(
        self,
        event_name,
        callback,
        temporary=False,
    ) -> int:
        """
        Register CDP event listener.

        Callback runs in background task to prevent blocking.

        Args:
            event_name: CDP event name (e.g., 'Page.loadEventFired').
            callback: Function called on event (sync or async).
            temporary: Remove after first invocation.

        Returns:
            Callback ID for removal.

        Note:
            Corresponding domain must be enabled before events fire.
        """

        async def callback_wrapper(event):
            pass

        if asyncio.iscoroutinefunction(callback):
            function_to_register = callback_wrapper
        else:
            function_to_register = callback

        logger.debug(
            f'Registering callback on tab: event={event_name}, temporary={temporary}, '
            f'async={asyncio.iscoroutinefunction(callback)}'
        )
        return await self._connection_handler.register_callback(
            event_name, function_to_register, temporary
        )

    async def remove_callback(self, callback_id: int):
        """Remove callback from tab."""
        logger.debug(f'Removing callback from tab: id={callback_id}')
        return await self._connection_handler.remove_callback(callback_id)

    async def clear_callbacks(self):
        """Clear all registered event callbacks."""
        logger.debug('Clearing all callbacks from tab')
        await self._connection_handler.clear_callbacks()

    def _get_connection_handler(self) -> ConnectionHandler:
        pass

    @staticmethod
    def _get_evaluate_command(
        script: str,
        *,
        object_group: Optional[str] = None,
        include_command_line_api: Optional[bool] = None,
        silent: Optional[bool] = None,
        context_id: Optional[int] = None,
        return_by_value: Optional[bool] = None,
        generate_preview: Optional[bool] = None,
        user_gesture: Optional[bool] = None,
        await_promise: Optional[bool] = None,
        throw_on_side_effect: Optional[bool] = None,
        timeout: Optional[float] = None,
        disable_breaks: Optional[bool] = None,
        repl_mode: Optional[bool] = None,
        allow_unsafe_eval_blocked_by_csp: Optional[bool] = None,
        unique_context_id: Optional[str] = None,
        serialization_options: Optional[SerializationOptions] = None,
    ):
        """Create an evaluate command with the given parameters."""
        return RuntimeCommands.evaluate(
            expression=script,
            object_group=object_group,
            include_command_line_api=include_command_line_api,
            silent=silent,
            context_id=context_id,
            return_by_value=return_by_value,
            generate_preview=generate_preview,
            user_gesture=user_gesture,
            await_promise=await_promise,
            throw_on_side_effect=throw_on_side_effect,
            timeout=timeout,
            disable_breaks=disable_breaks,
            repl_mode=repl_mode,
            allow_unsafe_eval_blocked_by_csp=allow_unsafe_eval_blocked_by_csp,
            unique_context_id=unique_context_id,
            serialization_options=serialization_options,
        )

    @staticmethod
    def _validate_argument_error(response: EvaluateResponse) -> None:
        """
        Validate that script didn't fail with ReferenceError about 'argument' being undefined.

        Raises:
            InvalidScriptWithElement: If script uses 'argument' keyword but no element was provided.
        """
        evaluate_result = response.get('result')
        if not isinstance(evaluate_result, dict):
            return

        remote_object = evaluate_result.get('result')
        if not isinstance(remote_object, dict):
            return

        if not (
            remote_object.get('type') == 'object'
            and remote_object.get('subtype') == 'error'
            and remote_object.get('className') == 'ReferenceError'
        ):
            return

        description = remote_object.get('description', '')
        if 'argument is not defined' in description:
            raise InvalidScriptWithElement('Script contains "argument" but no element was provided')

    _PAGE_LOAD_EVENT_MAP = {
        PageLoadState.INTERACTIVE: PageEvent.DOM_CONTENT_EVENT_FIRED,
        PageLoadState.COMPLETE: PageEvent.LOAD_EVENT_FIRED,
    }

    @asynccontextmanager
    async def _wait_page_load(self, timeout: int = 300):
        """Wait for page to reach the configured load state using CDP events.

        Registers a CDP event listener **before** yielding so the navigation
        command can be issued inside the ``async with`` block without race
        conditions.  This replaces the former ``document.readyState`` polling
        loop, eliminating the dependency on ``Runtime.evaluate`` during page
        load and the risk of inner command timeouts.

        The CDP event used depends on ``browser.options.page_load_state``:

        * ``INTERACTIVE`` — waits for ``Page.domContentEventFired``.
        * ``COMPLETE`` — waits for ``Page.loadEventFired``.

        Args:
            timeout: Maximum seconds to wait for the target load state.

        Raises:
            PageLoadTimeout: If the page doesn't reach the target state in time.
        """
        pass

    async def _find_cloudflare_shadow_root(self, timeout: float) -> ShadowRoot:
        """Poll for the Cloudflare Turnstile shadow root.

        Repeatedly calls ``find_shadow_roots(deep=False)`` and checks each
        shadow root's ``inner_html`` for the Cloudflare challenge domain.

        Args:
            timeout: Maximum seconds to wait for the shadow root.

        Returns:
            The first ShadowRoot whose inner HTML contains
            ``challenges.cloudflare.com``.

        Raises:
            WaitElementTimeout: If no matching shadow root is found within
                *timeout* seconds.
        """
        pass

    async def _bypass_cloudflare(
        self,
        event: dict,
        time_to_wait_captcha: float = 5,
    ) -> None:
        """Attempt to bypass Cloudflare Turnstile captcha via shadow root traversal.

        Traverses shadow roots to locate the Cloudflare iframe, navigates into
        it, and clicks the actual checkbox element (``span.cb-i``).
        """
        pass


class _DownloadHandle:
    """Handle returned by expect_download to access the downloaded file."""

    def __init__(
        self,
        state: dict[str, Any],
        will_begin_future: asyncio.Future[bool],
        done_future: asyncio.Future[bool],
        timeout: float,
    ) -> None:
        self._state = state
        self._will_begin_future = will_begin_future
        self._done_future = done_future
        self._timeout = timeout

    @property
    def file_path(self) -> Optional[str]:
        pass

    async def wait_started(self, timeout: Optional[float] = None) -> None:
        pass

    async def wait_finished(self, timeout: Optional[float] = None) -> None:
        pass

    async def read_bytes(self) -> bytes:
        pass

    async def read_base64(self) -> str:
        pass
