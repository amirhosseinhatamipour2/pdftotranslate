"""Shared data models for extracted PDF projects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TextSpan:
    """A single styled text run extracted from a PDF."""

    id: str
    text: str
    bbox: list[float]
    font: str
    size: float
    color: str
    flags: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "bbox": self.bbox,
            "font": self.font,
            "size": self.size,
            "color": self.color,
            "flags": self.flags,
        }


@dataclass(slots=True)
class PageData:
    """All assets and text spans needed to rebuild one PDF page in HTML."""

    number: int
    width: float
    height: float
    background: str
    spans: list[TextSpan] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "number": self.number,
            "width": self.width,
            "height": self.height,
            "background": self.background,
            "spans": [span.to_dict() for span in self.spans],
        }
