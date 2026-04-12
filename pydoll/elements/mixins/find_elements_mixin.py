from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Optional, Union, cast, overload

from pydoll.commands import (
    DomCommands,
    RuntimeCommands,
)
from pydoll.connection.connection_handler import ConnectionHandler
from pydoll.constants import By, Scripts
from pydoll.elements.utils import SelectorParser
from pydoll.exceptions import ElementNotFound, WaitElementTimeout

if TYPE_CHECKING:
    from typing import Literal, Optional, Union

    from pydoll.elements.web_element import WebElement
    from pydoll.interactions.iframe import IFrameContext
    from pydoll.protocol.base import Command, T_CommandParams, T_CommandResponse
    from pydoll.protocol.dom.methods import DescribeNodeResponse
    from pydoll.protocol.dom.types import Node
    from pydoll.protocol.runtime.methods import (
        CallFunctionOnParams,
        CallFunctionOnResponse,
        EvaluateParams,
        EvaluateResponse,
        GetPropertiesResponse,
    )


logger = logging.getLogger(__name__)


def create_web_element(*args, **kwargs):
    """
    Create WebElement instance avoiding circular imports.

    Factory method that dynamically imports WebElement at runtime
    to prevent circular import dependencies.
    """
    pass


class FindElementsMixin:
    """
    Mixin providing comprehensive element finding and waiting capabilities.

    Implements DOM element location using various selector strategies (CSS, XPath, etc.)
    with support for single/multiple element finding and configurable waiting.
    Classes using this mixin gain powerful element discovery without implementing
    complex location logic themselves.
    """

    _css_only: bool = False

    if TYPE_CHECKING:
        _connection_handler: ConnectionHandler

    @staticmethod
    def _build_text_expression(selector: str, method: str) -> Optional[str]:
        """
        Build JS expression using Scripts to extract textContent based on selector type.
        """
        pass

    @overload
    async def find(
        self,
        id: Optional[str] = ...,
        class_name: Optional[str] = ...,
        name: Optional[str] = ...,
        tag_name: Optional[str] = ...,
        text: Optional[str] = ...,
        timeout: int = ...,
        find_all: Literal[False] = False,
        raise_exc: Literal[True] = True,
        **attributes,
    ) -> WebElement: ...

    @overload
    async def find(
        self,
        id: Optional[str] = ...,
        class_name: Optional[str] = ...,
        name: Optional[str] = ...,
        tag_name: Optional[str] = ...,
        text: Optional[str] = ...,
        timeout: int = ...,
        find_all: Literal[False] = False,
        raise_exc: Literal[False] = False,
        **attributes,
    ) -> Optional[WebElement]: ...

    @overload
    async def find(
        self,
        id: Optional[str] = ...,
        class_name: Optional[str] = ...,
        name: Optional[str] = ...,
        tag_name: Optional[str] = ...,
        text: Optional[str] = ...,
        timeout: int = ...,
        find_all: Literal[True] = True,
        raise_exc: Literal[True] = True,
        **attributes,
    ) -> list[WebElement]: ...

    @overload
    async def find(
        self,
        id: Optional[str] = ...,
        class_name: Optional[str] = ...,
        name: Optional[str] = ...,
        tag_name: Optional[str] = ...,
        text: Optional[str] = ...,
        timeout: int = ...,
        find_all: Literal[True] = True,
        raise_exc: Literal[False] = False,
        **attributes,
    ) -> Optional[list[WebElement]]: ...

    @overload
    async def find(
        self,
        id: Optional[str] = ...,
        class_name: Optional[str] = ...,
        name: Optional[str] = ...,
        tag_name: Optional[str] = ...,
        text: Optional[str] = ...,
        timeout: int = ...,
        find_all: bool = ...,
        raise_exc: bool = ...,
        **attributes,
    ) -> Union[WebElement, list[WebElement], None]: ...

    async def find(
        self,
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        name: Optional[str] = None,
        tag_name: Optional[str] = None,
        text: Optional[str] = None,
        timeout: int = 0,
        find_all: bool = False,
        raise_exc: bool = True,
        **attributes: dict[str, str],
    ) -> Union[WebElement, list[WebElement], None]:
        """
        Find element(s) using combination of common HTML attributes.

        Flexible element location using standard attributes. Multiple attributes
        can be combined for specific selectors (builds XPath when multiple specified).

        Args:
            id: Element ID attribute value.
            class_name: CSS class name to match.
            name: Element name attribute value.
            tag_name: HTML tag name (e.g., "div", "input").
            text: Text content to match within element.
            timeout: Maximum seconds to wait for elements to appear.
            find_all: If True, returns all matches; if False, first match only.
            raise_exc: Whether to raise exception if no elements found.
            **attributes: Additional HTML attributes to match.

        Returns:
            WebElement, list[WebElement], or None based on find_all and raise_exc.

        Raises:
            ValueError: If no search criteria provided.
            ElementNotFound: If no elements found and raise_exc=True.
            WaitElementTimeout: If timeout specified and no elements appear in time.
            NotImplementedError: If called on a ShadowRoot (use query() with CSS instead).
        """
        pass

    @overload
    async def query(
        self,
        expression: str,
        timeout: int = ...,
        find_all: Literal[False] = False,
        raise_exc: Literal[True] = True,
    ) -> WebElement: ...

    @overload
    async def query(
        self,
        expression: str,
        timeout: int = ...,
        find_all: Literal[False] = False,
        raise_exc: Literal[False] = False,
    ) -> Optional[WebElement]: ...

    @overload
    async def query(
        self,
        expression: str,
        timeout: int = ...,
        find_all: Literal[True] = True,
        raise_exc: Literal[True] = True,
    ) -> list[WebElement]: ...

    @overload
    async def query(
        self,
        expression: str,
        timeout: int = ...,
        find_all: Literal[True] = True,
        raise_exc: Literal[False] = False,
    ) -> Optional[list[WebElement]]: ...

    @overload
    async def query(
        self,
        expression: str,
        timeout: int = ...,
        find_all: bool = ...,
        raise_exc: bool = ...,
    ) -> Union[WebElement, list[WebElement], None]: ...

    async def query(
        self, expression: str, timeout: int = 0, find_all: bool = False, raise_exc: bool = True
    ) -> Union[WebElement, list[WebElement], None]:
        """
        Find element(s) using raw CSS selector or XPath expression.

        Direct access using CSS or XPath syntax. Selector type automatically
        determined based on expression pattern.

        Args:
            expression: Selector expression (CSS, XPath, ID with #, class with .).
            timeout: Maximum seconds to wait for elements to appear.
            find_all: If True, returns all matches; if False, first match only.
            raise_exc: Whether to raise exception if no elements found.

        Returns:
            WebElement, list[WebElement], or None based on find_all and raise_exc.

        Raises:
            ElementNotFound: If no elements found and raise_exc=True.
            WaitElementTimeout: If timeout specified and no elements appear in time.
            NotImplementedError: If called with XPath on a ShadowRoot.
        """
        pass

    async def find_or_wait_element(
        self,
        by: By,
        value: str,
        timeout: int = 0,
        find_all: bool = False,
        raise_exc: bool = True,
    ) -> Union[WebElement, list[WebElement], None]:
        """
        Core element finding method with optional waiting capability.

        Searches for elements with flexible waiting. If timeout specified,
        repeatedly attempts to find elements with 0.5s delays until success or timeout.
        Used by higher-level find() and query() methods.

        Args:
            by: Selector strategy (CSS_SELECTOR, XPATH, ID, etc.).
            value: Selector value to locate element(s).
            timeout: Maximum seconds to wait (0 = no waiting).
            find_all: If True, returns all matches; if False, first match only.
            raise_exc: Whether to raise exception if no elements found.

        Returns:
            WebElement, list[WebElement], or None based on find_all and raise_exc.

        Raises:
            ElementNotFound: If no elements found with timeout=0 and raise_exc=True.
            WaitElementTimeout: If elements not found within timeout and raise_exc=True.
        """
        pass

    async def _find_across_iframes(
        self,
        segments: list[tuple[By, str]],
        timeout: int,
        find_all: bool,
        raise_exc: bool,
    ) -> Union[WebElement, list[WebElement], None]:
        """
        Retry loop for iframe-crossing element searches.

        Repeatedly calls :meth:`_attempt_find_across_iframes` until the target
        element is found or the *timeout* expires.

        Args:
            segments: Ordered ``(By, selector)`` pairs — one per iframe boundary
                plus a final selector for the target element(s).
            timeout: Maximum seconds to wait (0 = single attempt).
            find_all: If ``True``, the last segment uses ``_find_elements``.
            raise_exc: Whether to raise on failure.

        Returns:
            The found element(s), or ``None`` / ``[]`` on failure.

        Raises:
            ElementNotFound: If ``timeout=0``, nothing found, and ``raise_exc=True``.
            WaitElementTimeout: If timeout expires and ``raise_exc=True``.
        """
        pass

    async def _attempt_find_across_iframes(
        self,
        segments: list[tuple[By, str]],
        find_all: bool,
    ) -> Union[WebElement, list[WebElement], None]:
        """
        Single attempt to walk iframe segments and find the target element.

        For each intermediate segment, finds a single iframe element and uses it
        as the search context for the next segment. The last segment respects
        *find_all*.

        Args:
            segments: Ordered ``(By, selector)`` pairs.
            find_all: Whether the final segment should return all matches.

        Returns:
            Found element(s) or ``None`` / ``[]`` if any intermediate step fails.
        """
        pass

    async def _find_element(
        self, by: By, value: str, raise_exc: bool = True
    ) -> Optional[WebElement]:
        """
        Find first element matching selector.

        Internal method performing actual element search. Can be called directly
        for fine-grained control. Searches in document context or relative to
        current element (when used from WebElement).

        Args:
            by: Selector strategy (CSS_SELECTOR, XPATH, ID, etc.).
            value: Selector value to locate element.
            raise_exc: Whether to raise ElementNotFound if not found.

        Returns:
            WebElement instance or None if not found and raise_exc=False.

        Raises:
            ElementNotFound: If element not found and raise_exc=True.
        """
        pass

    async def _find_elements(self, by: By, value: str, raise_exc: bool = True) -> list[WebElement]:
        """
        Find all elements matching selector.

        Internal method performing actual multi-element search. Can be called directly
        for fine-grained control. Searches in document context or relative to
        current element (when used from WebElement).

        Args:
            by: Selector strategy (CSS_SELECTOR, XPATH, ID, etc.).
            value: Selector value to locate elements.
            raise_exc: Whether to raise ElementNotFound if none found.

        Returns:
            list of WebElement instances (empty if none found and raise_exc=False).

        Raises:
            ElementNotFound: If no elements found and raise_exc=True.
        """
        pass

    async def _get_object_attributes(self, object_id: str) -> list[str]:
        """
        Get attributes of a DOM node.
        """
        pass

    def _get_by_and_value(
        self,
        by_map: dict[str, By],
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        name: Optional[str] = None,
        tag_name: Optional[str] = None,
        text: Optional[str] = None,
        **attributes,
    ) -> tuple[By, str]:
        """
        Determine appropriate selector strategy and value from provided arguments.

        For single attribute: uses direct selector strategy.
        For multiple attributes: builds XPath expression.
        """
        pass

    @staticmethod
    def _build_xpath(
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        name: Optional[str] = None,
        tag_name: Optional[str] = None,
        text: Optional[str] = None,
        **attributes: str,
    ) -> str:
        """
        Build XPath expression from multiple attribute criteria.

        Constructs complex XPath combining multiple conditions with 'and' operators.
        Handles class names correctly for space-separated class lists.
        Uses contains() for text matching (partial text support).

        Note:
            Attribute names with underscores are automatically converted to hyphens
            to match HTML attribute naming conventions (e.g., data_test -> data-test).
        """
        pass

    @staticmethod
    def _get_expression_type(expression: str) -> By:
        """
        Auto-detect selector type from expression syntax.

        Patterns:
        - XPath: starts with ./, or /
        - Default: CSS_SELECTOR
        """
        pass

    async def _describe_node(self, object_id: str = '') -> Node:
        """
        Get detailed DOM node information using CDP DOM.describeNode.

        Used internally to gather data for WebElement initialization.
        """
        pass

    def _apply_iframe_context_to_element(
        self, element: WebElement, iframe_context: IFrameContext | None
    ) -> None:
        """
        Propagate iframe context to the newly created element.
        - If the element is also an iframe, configure session routing.
        - Otherwise, inject the iframe's own context.
        """
        pass

    def _resolve_routing(self) -> tuple[ConnectionHandler, Optional[str]]:
        """
        Resolve handler and sessionId for the current context (iframe routed or default).
        """
        iframe_context = getattr(self, '_iframe_context', None)
        if iframe_context and getattr(iframe_context, 'session_handler', None):
            return iframe_context.session_handler, getattr(iframe_context, 'session_id', None)
        routing_handler = getattr(self, '_routing_session_handler', None)
        if routing_handler is not None:
            return routing_handler, getattr(self, '_routing_session_id', None)
        return self._connection_handler, None

    async def _execute_command(
        self, command: Command[T_CommandParams, T_CommandResponse]
    ) -> T_CommandResponse:
        """Execute CDP command via resolved handler (60s timeout)."""
        handler, session_id = self._resolve_routing()
        if session_id:
            command['sessionId'] = session_id
        return await handler.execute_command(command, timeout=60)

    def _get_find_element_command(
        self,
        by: By,
        value: str,
        object_id: str = '',
        execution_context_id: Optional[int] = None,
    ):
        """
        Create CDP command for finding single element.

        Handles special cases for different selector types and contexts:
        - CLASS_NAME/ID: converts to CSS selector
        - Relative searches: uses different scripts for context element
        - XPath: requires special handling
        - NAME: converts to XPath expression
        """
        pass

    def _get_find_elements_command(
        self,
        by: By,
        value: str,
        object_id: str = '',
        execution_context_id: Optional[int] = None,
    ):
        """
        Create CDP command for finding multiple elements.

        Similar to _get_find_element_command but for multiple element searches.
        Handles same special cases and selector type conversions.
        """
        pass

    def _get_find_element_by_xpath_command(
        self,
        xpath: str,
        object_id: str,
        execution_context_id: Optional[int] = None,
    ):
        """
        Create CDP command specifically for XPath single element finding.

        XPath requires special handling vs CSS selectors. Ensures relative
        XPath for context-based searches.
        """
        pass

    def _get_find_elements_by_xpath_command(
        self,
        xpath: str,
        object_id: str,
        execution_context_id: Optional[int] = None,
    ):
        """
        Create CDP command specifically for XPath multiple element finding.

        XPath requires special handling vs CSS selectors. Ensures relative
        XPath for context-based searches.
        """
        pass

    @staticmethod
    def _ensure_relative_xpath(xpath: str) -> str:
        """
        Ensure XPath is relative by prepending dot if needed.

        Converts absolute XPath to relative for context-based searches.
        """
        pass

    @staticmethod
    def _has_object_id_key(response: Union[EvaluateResponse, CallFunctionOnResponse]) -> bool:
        """
        Check if response has objectId key.
        """
        pass
