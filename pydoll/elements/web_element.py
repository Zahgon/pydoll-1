from __future__ import annotations

import asyncio
import json
import logging
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import aiofiles

from pydoll.commands import (
    DomCommands,
    InputCommands,
    PageCommands,
    RuntimeCommands,
)
from pydoll.connection import ConnectionHandler
from pydoll.constants import (
    Key,
    Scripts,
)
from pydoll.elements.mixins import FindElementsMixin
from pydoll.elements.shadow_root import ShadowRoot
from pydoll.exceptions import (
    ElementNotAFileInput,
    ElementNotFound,
    ElementNotInteractable,
    ElementNotVisible,
    InvalidFileExtension,
    InvalidIFrame,
    MissingScreenshotPath,
    ShadowRootNotFound,
    WaitElementTimeout,
)
from pydoll.interactions.iframe import IFrameContext, IFrameContextResolver
from pydoll.interactions.keyboard import Keyboard
from pydoll.protocol.dom.types import ShadowRootType
from pydoll.protocol.input.types import (
    KeyEventType,
    KeyModifier,
    MouseButton,
    MouseEventType,
)
from pydoll.protocol.page.types import ScreenshotFormat, Viewport
from pydoll.protocol.runtime.methods import (
    CallFunctionOnResponse,
    EvaluateResponse,
    GetPropertiesResponse,
    SerializationOptions,
)
from pydoll.protocol.runtime.types import CallArgument
from pydoll.utils import (
    decode_base64_to_bytes,
    extract_text_from_html,
    is_script_already_function,
)

if TYPE_CHECKING:
    from pydoll.interactions.mouse import Mouse as MouseType
    from pydoll.protocol.dom.methods import (
        DescribeNodeResponse,
        GetBoxModelResponse,
        GetOuterHTMLResponse,
        ResolveNodeResponse,
    )
    from pydoll.protocol.dom.types import Quad
    from pydoll.protocol.page.methods import CaptureScreenshotResponse
    from pydoll.protocol.runtime.methods import GetPropertiesResponse

logger = logging.getLogger(__name__)


class WebElement(FindElementsMixin):  # noqa: PLR0904
    """
    DOM element wrapper for browser automation.

    Provides comprehensive functionality for element interaction, inspection,
    and manipulation using Chrome DevTools Protocol commands.
    """

    if TYPE_CHECKING:
        _routing_session_handler: Optional[ConnectionHandler]
        _routing_session_id: Optional[str]
        _routing_parent_frame_id: Optional[str]

    def __init__(
        self,
        object_id: str,
        connection_handler: ConnectionHandler,
        method: Optional[str] = None,
        selector: Optional[str] = None,
        attributes_list: list[str] = [],
        mouse: Optional['MouseType'] = None,
    ):
        """
        Initialize WebElement wrapper.

        Args:
            object_id: Unique CDP object identifier for this DOM element.
            connection_handler: Connection instance for browser communication.
            method: Search method used to find this element (for debugging).
            selector: Selector string used to find this element (for debugging).
            attributes_list: Flat list of alternating attribute names and values.
            mouse: Optional Mouse instance for humanized click behavior.

        Note:
            Mouse and Keyboard follow different ownership strategies. Mouse is a shared
            instance from Tab, passed down to elements to preserve cursor position state
            across interactions. It dispatches commands through Tab._execute_command, which
            means it has no iframe context awareness. Keyboard is created per-element and
            routes commands through the element's own _execute_command, correctly handling
            iframe routing. For iframe elements, the mouse is intentionally skipped during
            humanized clicks (see click()) to avoid dispatching events to the wrong frame.
        """
        self._object_id = object_id
        self._search_method = method
        self._selector = selector
        self._connection_handler = connection_handler
        self._attributes: dict[str, str] = {}
        self._keyboard: Optional[Keyboard] = None
        self._mouse = mouse
        self._iframe_context: Optional[IFrameContext] = None
        self._iframe_resolver: Optional[IFrameContextResolver] = None
        self._def_attributes(attributes_list)
        logger.debug(
            f'WebElement initialized: object_id={self._object_id}, '
            f'method={self._search_method}, selector={self._selector}, '
            f'attributes={len(self._attributes)}'
        )

    def _get_keyboard(self) -> Keyboard:
        """Get or create the keyboard controller."""
        pass

    def _get_iframe_resolver(self) -> IFrameContextResolver:
        """Get or create the iframe context resolver."""
        pass

    @property
    def attributes(self) -> dict[str, str]:
        """Read-only copy of the element's cached attributes."""
        pass

    @property
    def value(self) -> Optional[str]:
        """Element's value attribute (for form elements)."""
        pass

    @property
    def class_name(self) -> Optional[str]:
        """Element's CSS class name(s)."""
        pass

    @property
    def id(self) -> Optional[str]:
        """Element's ID attribute."""
        pass

    @property
    def tag_name(self) -> Optional[str]:
        """Element's HTML tag name."""
        pass

    @property
    def is_iframe(self) -> bool:
        """Whether the element represents an iframe."""
        pass

    @property
    def is_enabled(self) -> bool:
        """Whether element is enabled (not disabled)."""
        pass

    @property
    async def text(self) -> str:
        """Visible text content of the element."""
        pass

    @property
    async def bounds(self) -> Quad:
        """
        Element's bounding box coordinates.

        Returns coordinates in CSS pixels relative to document origin.
        """
        pass

    @property
    async def inner_html(self) -> str:
        pass

    @property
    async def iframe_context(self) -> Optional[IFrameContext]:
        """
        Return the resolved iframe context for this element when it is an <iframe>.

        The context includes: frame_id, document_url, execution_context_id,
        document_object_id and, for OOPIF targets, the session_id and
        session_handler used for routing commands. The context is always freshly
        resolved to avoid stale execution contexts after iframe navigations or
        reloads. Non-iframe elements return None.

        Returns:
            IFrameContext | None: Resolved iframe context or None for non-iframes.
        """
        pass

    def get_attribute(self, name: str) -> Optional[str]:
        """
        Get element attribute value.

        Note:
            Only provides attributes available when element was located.
            For dynamic attributes, consider using JavaScript execution.
        """
        pass

    async def get_bounds_using_js(self) -> dict[str, int]:
        """
        Get element bounds using JavaScript getBoundingClientRect().

        Returns coordinates relative to viewport (alternative to bounds property).
        """
        pass

    async def get_parent_element(self) -> WebElement:
        """Element's parent element."""
        pass

    async def get_shadow_root(self, timeout: float = 0) -> ShadowRoot:
        """
        Get the shadow root attached to this element.

        Args:
            timeout: Maximum seconds to wait for the shadow root to appear.
                When > 0, repeatedly polls (every 0.5s) until a shadow root
                is found or the timeout expires.

        Returns:
            ShadowRoot instance for traversing the shadow DOM.

        Raises:
            ShadowRootNotFound: If no shadow root is attached (when timeout=0).
            WaitElementTimeout: If timeout > 0 and no shadow root appears
                within the specified duration.
        """
        pass

    async def _get_shadow_root(self) -> ShadowRoot:
        """Get the shadow root attached to this element (single attempt)."""
        pass

    async def get_children_elements(
        self, max_depth: int = 1, tag_filter: list[str] = [], raise_exc: bool = False
    ) -> list[WebElement]:
        """
        Retrieve all direct and nested child elements of this element.

        Args:
            max_depth (int, optional): Maximum depth to traverse when finding children.
                Defaults to 1 for direct children only.
            tag_filter (list[str], optional): List of HTML tag names to filter results.
                If empty, returns all child elements regardless of tag. Defaults to [].

        Returns:
            list[WebElement]: List of child WebElement objects found within the specified
                depth and matching the tag filter criteria.

        Raises:
            ElementNotFound: If no child elements are found for this element and raise_exc is True.
        """
        pass

    async def get_siblings_elements(
        self, tag_filter: list[str] = [], raise_exc: bool = False
    ) -> list[WebElement]:
        """
        Retrieve all sibling elements of this element (elements at the same DOM level).

        Args:
            tag_filter (list[str], optional): List of HTML tag names to filter results.
                If empty, returns all sibling elements regardless of tag. Defaults to [].

        Returns:
            list[WebElement]: List of sibling WebElement objects that share the same
                parent as this element and match the tag filter criteria.

        Raises:
            ElementNotFound: If no sibling elements are found for this element
            and raise_exc is True.
        """
        pass

    async def take_screenshot(
        self,
        path: Optional[str | Path] = None,
        quality: int = 100,
        as_base64: bool = False,
    ) -> Optional[str]:
        """
        Capture screenshot of this element only.

        Automatically scrolls element into view before capturing.

        Args:
            path: File path for screenshot (extension determines format).
            quality: Image quality 0-100 (default 100).
            as_base64: Return as base64 string instead of saving file.

        Returns:
            Base64 screenshot data if as_base64=True, None otherwise.

        Raises:
            InvalidFileExtension: If file extension not supported.
            MissingScreenshotPath: If path is None and as_base64 is False.
        """
        pass

    async def scroll_into_view(self):
        """Scroll element into visible viewport."""
        pass

    async def wait_until(
        self,
        *,
        is_visible: bool = False,
        is_interactable: bool = False,
        timeout: int = 0,
    ):
        """Wait for element to meet specified conditions.

        Raises:
            ValueError: If neither ``is_visible`` nor ``is_interactable`` is True.
            WaitElementTimeout: If the condition is not met within ``timeout``.
        """
        pass

    async def click_using_js(self):
        """
        Click element using JavaScript click() method.

        Raises:
            ElementNotVisible: If element is not visible.
            ElementNotInteractable: If element couldn't be clicked.

        Note:
            For <option> elements, uses specialized selection approach.
            Element is automatically scrolled into view.
        """
        pass

    async def click(
        self,
        x_offset: int = 0,
        y_offset: int = 0,
        hold_time: float = 0.1,
        humanize: bool = False,
    ):
        """
        Click element using simulated mouse events.

        Args:
            x_offset: Horizontal offset from element center.
            y_offset: Vertical offset from element center.
            hold_time: Duration to hold mouse button down (used when humanize=False).
            humanize: When True and a Mouse instance is available, uses humanized
                Bezier curve movement from the current tracked position to the
                element center before clicking. When False, dispatches raw CDP
                mousePressed/mouseReleased events directly.

        Raises:
            ElementNotVisible: If element is not visible.

        Note:
            For <option> elements, delegates to specialized JavaScript approach.
            Element is automatically scrolled into view.
        """
        pass

    async def focus(self):
        """Focus this element via CDP DOM.focus command."""
        pass

    async def clear(self):
        """
        Clear the current value of the element.

        Supports standard inputs, textareas, and contenteditable elements.
        Dispatches ``input`` and ``change`` events so frameworks detect the update.

        Raises:
            ElementNotInteractable: If the element does not accept text input.
        """
        logger.info('Clearing element value')
        result = await self.execute_script(Scripts.CLEAR_INPUT, return_by_value=True)
        success = result['result'].get('result', {}).get('value', False)
        if not success:
            logger.error('Element does not accept text input')
            raise ElementNotInteractable('Element does not accept text input')
        if self._attributes.get('tag_name', '').lower() in {'input', 'textarea'}:
            self._attributes['value'] = ''

    async def insert_text(self, text: str):
        """
        Insert text into element using JavaScript.

        Supports standard inputs, textareas, contenteditable elements, and rich text editors.
        Inserts text at cursor position or replaces selected text.

        Args:
            text: Text to insert.

        Raises:
            ElementNotInteractable: If element does not accept text input.

        Note:
            Uses JavaScript for maximum compatibility with all input types.
            Automatically handles input/textarea and contenteditable elements.
        """
        pass

    async def set_input_files(self, files: str | Path | list[str | Path]):
        """
        Set file paths for file input element.

        Args:
            files: list of absolute file paths to existing files.

        Raises:
            ElementNotAFileInput: If element is not a file input.
        """
        pass

    async def type_text(
        self,
        text: str,
        humanize: bool = False,
        interval: Optional[float] = None,
    ):
        """
        Type text character by character.

        Args:
            text: Text to type into the element.
            humanize: When True, simulates human-like typing.
            interval: Deprecated. Use humanize=True instead.
        """
        pass

    async def key_down(self, key: Key, modifiers: Optional[KeyModifier] = None):
        """
        Send key down event.

        .. deprecated::
            This method is deprecated. Use ``tab.keyboard.down()`` instead.

        Note:
            Only sends key down without release. Pair with key_up() for complete keypress.
        """
        pass

    async def key_up(self, key: Key):
        """
        Send key up event (should follow corresponding key_down()).

        .. deprecated::
            This method is deprecated. Use ``tab.keyboard.up()`` instead.
        """
        pass

    async def press_keyboard_key(
        self,
        key: Key,
        modifiers: Optional[KeyModifier] = None,
        interval: float = 0.1,
    ):
        """
        Press and release keyboard key with configurable timing.

        .. deprecated::
            This method is deprecated. Use ``tab.keyboard.press()`` instead.

        Better for special keys (Enter, Tab, etc.) than type_text().
        """
        pass

    async def is_editable(self) -> bool:
        """
        Check if element can accept text input.

        Returns:
            True if element is editable (input, textarea, or contenteditable).
        """
        pass

    async def is_visible(self):
        """Check if element is visible using comprehensive JavaScript visibility test."""
        pass

    async def is_on_top(self):
        """Check if element is topmost at its center point (not covered by overlays)."""
        pass

    async def is_interactable(self):
        """Check if element is interactable based on visibility and position."""
        pass

    async def execute_script(
        self,
        script: str,
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
    ) -> CallFunctionOnResponse:
        """
        Execute JavaScript in element context.

        Args:
            script (str): JavaScript code to execute. Use 'this' to reference this element.
            arguments (Optional[list[CallArgument]]): Arguments to pass to the function
                (Runtime.callFunctionOn).
            silent (Optional[bool]): Whether to silence exceptions (Runtime.callFunctionOn).
            return_by_value (Optional[bool]): Whether to return the result by value instead of
                reference (Runtime.callFunctionOn).
            generate_preview (Optional[bool]): Whether to generate a preview for the result
                (Runtime.callFunctionOn).
            user_gesture (Optional[bool]): Whether to treat the call as initiated by user
                gesture (Runtime.callFunctionOn).
            await_promise (Optional[bool]): Whether to await promise result
                (Runtime.callFunctionOn).
            execution_context_id (Optional[int]): ID of the execution context to call the
                function in (Runtime.callFunctionOn).
            object_group (Optional[str]): Symbolic group name for the result
                (Runtime.callFunctionOn).
            throw_on_side_effect (Optional[bool]): Whether to throw if side effect cannot be
                ruled out (Runtime.callFunctionOn).
            unique_context_id (Optional[str]): Unique context ID for the function call
                (Runtime.callFunctionOn).
            serialization_options (Optional[SerializationOptions]): Serialization options for
                the result (Runtime.callFunctionOn).

        Returns:
            CallFunctionOnResponse: The result of the script execution.

        Examples:
            # Click the element
            await element.execute_script('this.click()')

            # Modify element style
            await element.execute_script('this.style.border = "2px solid red"')

            # Get element text
            result = await element.execute_script('return this.textContent', return_by_value=True)

            # Set element content
            await element.execute_script('this.textContent = "Hello World"')
        """
        if not is_script_already_function(script):
            script = f'function(){{ {script} }}'

        logger.debug(
            f'Executing script on element: return_by_value={return_by_value}, '
            f'length={len(script)}, args={len(arguments) if arguments else 0}'
        )
        command = RuntimeCommands.call_function_on(
            function_declaration=script,
            object_id=self._object_id,
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
        return await self._execute_command(command)

    def __repr__(self):
        """String representation showing attributes and object ID."""
        attrs = ', '.join(f'{k}={v!r}' for k, v in self._attributes.items())
        return f'{self.__class__.__name__}({attrs})(object_id={self._object_id})'

    def _is_inside_iframe(self) -> bool:
        """Check if this element is inside an iframe context (not the iframe itself)."""
        pass

    async def _get_iframe_inner_html(self) -> str:
        """Get inner HTML of an iframe element."""
        pass

    def _apply_routing_from_context(self) -> None:
        """Apply routing attributes from iframe context.

        After iframe context resolution, commands targeting the *content* of
        the iframe should route through ``_iframe_context`` (handled by
        ``_resolve_routing`` which prioritises ``_iframe_context`` over
        ``_routing_session_*``).

        The ``_routing_session_handler`` / ``_routing_session_id`` attributes
        must be preserved: they identify the parent OOPIF session where the
        ``<iframe>`` *element itself* lives.  The resolver needs them to
        re-describe the element on subsequent re-resolutions.
        """

    async def _click_option_tag(self):
        """Specialized method for clicking <option> elements in dropdowns."""
        pass

    async def _get_family_elements(
        self, script: str, max_depth: int = 1, tag_filter: list[str] = []
    ) -> list[WebElement]:
        """
        Retrieve all family elements of this element (elements at the same DOM level).

        Args:
            script (str): CDP script to execute for retrieving family elements.
            tag_filter (list[str], optional): List of HTML tag names to filter results.
                If empty, returns all family elements regardless of tag. Defaults to [].

        Returns:
            list[WebElement]: List of family WebElement objects that share the same
                parent as this element and match the tag filter criteria.
        """
        pass

    def _def_attributes(self, attributes_list: list[str]):
        """Process flat attribute list into dictionary (renames 'class' to 'class_name')."""
        pass

    def _is_option_tag(self):
        """Check if element is an <option> tag."""
        pass

    async def _is_option_element(self) -> bool:
        """
        Robust check for <option> elements, falling back to JS when tag_name is missing.
        """
        pass

    @staticmethod
    def _calculate_center(bounds: list) -> tuple:
        """Calculate center point from bounding box coordinates."""
        pass
