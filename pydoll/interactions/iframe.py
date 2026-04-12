from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, Optional

from pydoll.commands import DomCommands, PageCommands, RuntimeCommands, TargetCommands
from pydoll.connection import ConnectionHandler
from pydoll.exceptions import InvalidIFrame
from pydoll.protocol.dom.methods import DescribeNodeResponse, GetFrameOwnerResponse
from pydoll.protocol.dom.types import Node
from pydoll.protocol.page.methods import CreateIsolatedWorldResponse, GetFrameTreeResponse
from pydoll.protocol.page.types import Frame, FrameTree
from pydoll.protocol.runtime.methods import EvaluateResponse
from pydoll.protocol.target.methods import AttachToTargetResponse, GetTargetsResponse

if TYPE_CHECKING:
    from pydoll.elements.web_element import WebElement

logger = logging.getLogger(__name__)


@dataclass
class IFrameContext:
    """Context information for an iframe element."""

    frame_id: str
    document_url: Optional[str] = None
    execution_context_id: Optional[int] = None
    document_object_id: Optional[str] = None
    session_handler: Optional[ConnectionHandler] = None
    session_id: Optional[str] = None


class IFrameContextResolver:
    """Resolves iframe context for WebElement."""

    def __init__(self, element: WebElement):
        self._element = element

    async def resolve(self) -> IFrameContext:
        """
        Resolve and return iframe context.

        Returns:
            IFrameContext with frame_id, document_url, execution_context_id,
            document_object_id and session info for OOPIF targets.

        Raises:
            InvalidIFrame: If unable to resolve the iframe context.
        """
        pass

    def _get_base_session(self) -> tuple[ConnectionHandler, Optional[str]]:
        """Return the default handler and session id for routing commands."""
        pass

    async def _describe_element_node(
        self,
        handler: ConnectionHandler,
        session_id: Optional[str],
    ) -> Node:
        """Describe the iframe element using the given handler/session.

        This bypasses ``_resolve_routing()`` which, after a previous
        resolution, may return the iframe *content* session instead of
        the parent session where the element actually lives.
        """
        pass

    @staticmethod
    def _extract_frame_metadata(
        node_info: Node,
    ) -> tuple[Optional[str], Optional[str], Optional[str], Optional[int]]:
        """Extract iframe-related metadata from DOM node info.

        Returns:
            Tuple of (frame_id, document_url, content_frame_id, backend_node_id).
            ``content_frame_id`` is the frame ID of the frame *created* by the
            ``<iframe>`` element (``node_info['frameId']`` on frame-owner
            elements).  For same-origin iframes it equals
            ``contentDocument.frameId``; for OOPIFs ``contentDocument`` is
            absent but ``content_frame_id`` is still set by the browser.
        """
        pass

    async def _resolve_frame_by_owner(
        self,
        base_handler: ConnectionHandler,
        base_session_id: Optional[str],
        backend_node_id: int,
        current_document_url: Optional[str],
    ) -> tuple[Optional[str], Optional[str]]:
        """Resolve frame id and URL by matching owner backend_node_id."""
        pass

    async def _find_frame_by_owner(
        self,
        handler: ConnectionHandler,
        session_id: Optional[str],
        backend_node_id: int,
    ) -> tuple[Optional[str], Optional[str]]:
        """Find frame by matching owner backend_node_id."""
        pass

    @staticmethod
    async def _get_frame_tree_for(
        handler: ConnectionHandler,
        session_id: Optional[str],
    ) -> FrameTree:
        """Get Page frame tree for the given connection/target."""
        pass

    @staticmethod
    def _walk_frames(tree: FrameTree) -> Iterable[Frame]:
        """Recursively traverse FrameTree and collect all frame descriptors."""
        pass

    @staticmethod
    async def _owner_backend_for(
        handler: ConnectionHandler,
        session_id: Optional[str],
        frame_id: str,
    ) -> Optional[int]:
        """Get backendNodeId of the DOM element that owns the given frame."""
        pass

    async def _resolve_oopif_if_needed(
        self,
        current_frame_id: Optional[str],
        content_frame_id: Optional[str],
        backend_node_id: Optional[int],
        current_document_url: Optional[str],
        base_handler: Optional[ConnectionHandler] = None,
        base_session_id: Optional[str] = None,
    ) -> tuple[Optional[ConnectionHandler], Optional[str], Optional[str], Optional[str]]:
        """Resolve OOPIF and routing when needed."""
        pass

    async def _resolve_oopif_by_parent(
        self,
        content_frame_id: str,
        backend_node_id: Optional[int],
        base_handler: Optional[ConnectionHandler] = None,
        base_session_id: Optional[str] = None,
    ) -> tuple[Optional[ConnectionHandler], Optional[str], Optional[str], Optional[str]]:
        """Resolve out-of-process iframe using content frame id.

        ``content_frame_id`` is the frame ID of the frame *created* by the
        ``<iframe>`` element (obtained from ``DOM.describeNode``'s
        ``node.frameId``).  For OOPIF targets the root frame of the target
        shares this ID, so we can match directly without needing
        ``DOM.getFrameOwner``.

        When a direct frame-ID match is not possible (e.g. nested sub-frames
        inside the OOPIF), the method falls back to ``DOM.getFrameOwner``
        using the routing handler/session that has DOM visibility into the
        parent context.
        """
        pass

    @staticmethod
    def _find_child_by_parent(tree: FrameTree, parent_id: str) -> Optional[str]:
        """Find id of child frame whose parentId equals the given one."""
        pass

    @staticmethod
    async def _create_isolated_world_for_frame(
        frame_id: str,
        handler: ConnectionHandler,
        session_id: Optional[str],
    ) -> int:
        """Create isolated world for the given frame."""
        pass

    async def _get_document_object_id(
        self,
        execution_context_id: int,
        context: IFrameContext,
    ) -> str:
        """Get document.documentElement object id in iframe context."""
        pass
