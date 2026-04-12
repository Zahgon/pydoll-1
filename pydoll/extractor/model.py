"""ExtractionModel base class for declarative data extraction."""

from __future__ import annotations

from typing import ClassVar, Optional

from pydantic import BaseModel, ConfigDict

from pydoll.extractor.exceptions import InvalidExtractionModel
from pydoll.extractor.field import ExtractionMetadata, pop_field_metadata


class ExtractionModel(BaseModel):
    """Base class for declarative extraction models.

    Inherits from pydantic.BaseModel, gaining automatic validation,
    type coercion, serialization (model_dump, model_dump_json), and
    JSON Schema generation (model_json_schema).

    Subclasses define fields using Field() descriptors with selectors
    and/or semantic descriptions. The extraction engine uses this
    metadata to extract structured data from web pages.

    Example::

        class Article(ExtractionModel):
            title: str = Field(selector='h1', description='Article title')
            author: str = Field(selector='.author', description='Author name')
    """

    _extraction_fields_cache: ClassVar[Optional[dict[str, ExtractionMetadata]]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def get_extraction_fields(cls) -> dict[str, ExtractionMetadata]:
        """Get extraction metadata for all fields, collecting lazily on first access.

        Each subclass gets its own cache, even if a parent class has already
        been collected. This ensures inherited fields are included correctly.

        Returns:
            Dictionary mapping field name to ExtractionMetadata.

        Raises:
            InvalidExtractionModel: If a field has metadata but lacks
                both selector and description.
        """
        pass


def _collect_extraction_metadata(
    cls: type[ExtractionModel],
) -> dict[str, ExtractionMetadata]:
    """Read ExtractionMetadata from pydantic FieldInfo objects via registry.

    For each field, checks if json_schema_extra contains an _extraction_key
    that maps to a registered ExtractionMetadata. Validates that each
    extraction field has at least a selector or a description.

    Args:
        cls: ExtractionModel subclass to inspect.

    Returns:
        Dictionary mapping field name to ExtractionMetadata.

    Raises:
        InvalidExtractionModel: If a field has metadata but lacks
            both selector and description.
    """
    pass
