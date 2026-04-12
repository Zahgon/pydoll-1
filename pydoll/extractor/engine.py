"""Extraction engine that orchestrates DOM querying and model building."""

from __future__ import annotations

import asyncio
import logging
import types
from collections.abc import Coroutine
from typing import TYPE_CHECKING, Optional, TypeVar, Union, get_args, get_origin

from pydoll.elements.mixins.find_elements_mixin import FindElementsMixin
from pydoll.elements.web_element import WebElement
from pydoll.extractor.exceptions import FieldExtractionFailed
from pydoll.extractor.field import ExtractionMetadata
from pydoll.extractor.model import ExtractionModel

if TYPE_CHECKING:
    from pydoll.browser.tab import Tab

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='ExtractionModel')


class ExtractionEngine:
    """Orchestrates extraction by querying the DOM and building model instances.

    Internal engine used by Tab.extract() and Tab.extract_all().
    Users do not interact with it directly.
    """

    def __init__(self, tab: Tab) -> None:
        self._tab = tab

    async def extract(
        self,
        model: type[T],
        *,
        scope: Optional[str] = None,
        timeout: int = 0,
    ) -> T:
        """Extract a single model instance from the page.

        Args:
            model: ExtractionModel subclass to populate.
            scope: Optional CSS/XPath selector to limit extraction region.
            timeout: Seconds to wait for elements to appear (0 = no wait).

        Returns:
            Populated model instance.

        Raises:
            FieldExtractionFailed: If a required field cannot be extracted.
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
        """Extract multiple model instances from repeated containers.

        Each element matching scope generates one model instance.

        Args:
            model: ExtractionModel subclass to populate.
            scope: CSS/XPath selector for the repeated container (required).
            timeout: Seconds to wait for elements to appear (0 = no wait).
            limit: Maximum number of items to extract (None = all).

        Returns:
            List of populated model instances.
        """
        pass

    async def _extract_fields(
        self,
        model: type[T],
        context: FindElementsMixin,
        timeout: int,
    ) -> dict[str, Union[str, int, float, bool, list[str], object]]:
        """Extract all fields from the DOM concurrently.

        Launches all field extractions in parallel using asyncio.gather,
        then collects results and handles errors per field.

        Args:
            model: ExtractionModel subclass with extraction fields.
            context: Tab or WebElement to scope queries within.
            timeout: Seconds to wait for each element to appear.

        Returns:
            Dictionary of field name -> extracted value.
        """
        pass

    async def _extract_field(
        self,
        metadata: ExtractionMetadata,
        annotation: type,
        context: FindElementsMixin,
        timeout: int,
    ) -> Union[str, int, float, bool, list[str], object]:
        """Extract a single field value from the DOM.

        Handles scalar types, list types, nested ExtractionModel,
        and list[ExtractionModel].

        Args:
            metadata: Extraction metadata with selector/attribute/transform.
            annotation: The field's resolved type annotation.
            context: Tab or WebElement to query within.
            timeout: Seconds to wait for the element to appear.

        Returns:
            Extracted and optionally transformed value.
        """
        pass

    async def _extract_list_field(
        self,
        metadata: ExtractionMetadata,
        annotation: type,
        context: FindElementsMixin,
        timeout: int,
    ) -> list[Union[str, int, float, bool, object]]:
        """Extract a list of values from multiple matching elements."""
        pass

    async def _extract_nested_model(
        self,
        metadata: ExtractionMetadata,
        model: type[T],
        context: FindElementsMixin,
        timeout: int,
    ) -> T:
        """Extract a nested ExtractionModel by scoping to the selector element."""
        pass


async def _extract_scalar_field(
    metadata: ExtractionMetadata,
    context: FindElementsMixin,
    timeout: int,
) -> Union[str, int, float, bool, object]:
    """Extract a single scalar value from the DOM."""
    pass


async def _extract_value(
    element: WebElement,
    metadata: ExtractionMetadata,
) -> str:
    """Read raw string value from a WebElement.

    If metadata.attribute is set, reads that HTML attribute.
    Otherwise reads element.text (innerText).

    Args:
        element: WebElement to read from.
        metadata: Field metadata with optional attribute name.

    Returns:
        Raw string value before transform.
    """
    pass


def _apply_transform(
    raw: str,
    metadata: ExtractionMetadata,
) -> Union[str, int, float, bool, object]:
    """Apply metadata.transform to the raw extracted string.

    Args:
        raw: Raw string from the DOM.
        metadata: Field metadata with optional transform callable.

    Returns:
        Transformed value, or raw string if no transform.
    """
    pass


def _build_instance(
    model: type[T],
    values: dict[str, Union[str, int, float, bool, list[str], object]],
) -> T:
    """Build model instance from extracted values.

    Pydantic handles validation, type coercion, and defaults.

    Args:
        model: ExtractionModel subclass.
        values: Field name -> value mapping.

    Returns:
        Populated model instance.

    Raises:
        FieldExtractionFailed: If pydantic validation fails.
    """
    pass


def _unwrap_optional(annotation: type) -> type:
    """Unwrap Optional[X] or X | None to X. Returns annotation unchanged otherwise.

    Handles both typing.Optional (Union) and PEP 604 syntax (types.UnionType).
    """
    pass


def _is_list_type(annotation: type) -> bool:
    """Check if annotation is list[X]."""
    pass


def _get_inner_type(annotation: type) -> type:
    """Get X from list[X]."""
    pass


def _is_extraction_model(annotation: type) -> bool:
    """Check if annotation is an ExtractionModel subclass."""
    pass
