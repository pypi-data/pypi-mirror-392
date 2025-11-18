"""Helpers for converting signature bounding boxes into PNG crops."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from .detector.file_result_model import FileResult
from .detector.signature_model import Signature

try:  # pragma: no cover - optional dependency
    import fitz  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    fitz = None  # type: ignore[misc]


class SignatureCroppingUnavailable(RuntimeError):
    """Raised when PNG cropping cannot be performed (e.g., PyMuPDF missing)."""


def crop_signatures(
    pdf_path: Path,
    file_result: FileResult,
    *,
    output_dir: Path,
    dpi: int = 200,
    logger: logging.Logger | None = None,
) -> list[Path]:
    """Render each signature bounding box to a PNG image using PyMuPDF."""

    if fitz is None:  # pragma: no cover - exercised when dependency absent
        raise SignatureCroppingUnavailable(
            "PyMuPDF is required for PNG crops. Install 'pymupdf' or 'sigdetect[pymupdf]'."
        )

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    with fitz.open(pdf_path) as document:  # type: ignore[attr-defined]
        per_document_dir = output_dir / pdf_path.stem
        per_document_dir.mkdir(parents=True, exist_ok=True)
        scale = dpi / 72.0
        matrix = fitz.Matrix(scale, scale)

        for index, signature in enumerate(file_result.Signatures, start=1):
            if not signature.BoundingBox or not signature.Page:
                continue
            try:
                page = document.load_page(signature.Page - 1)
            except Exception as exc:  # pragma: no cover - defensive
                if logger:
                    logger.warning(
                        "Failed to load page for signature crop",
                        extra={
                            "file": pdf_path.name,
                            "page": signature.Page,
                            "error": str(exc),
                        },
                    )
                continue

            clip = _to_clip_rect(page, signature.BoundingBox)
            if clip is None:
                continue

            filename = _build_filename(index, signature)
            destination = per_document_dir / filename

            try:
                pixmap = page.get_pixmap(matrix=matrix, clip=clip, alpha=False)
                pixmap.save(destination)
            except Exception as exc:  # pragma: no cover - defensive
                if logger:
                    logger.warning(
                        "Failed to render signature crop",
                        extra={
                            "file": pdf_path.name,
                            "page": signature.Page,
                            "field": signature.FieldName,
                            "error": str(exc),
                        },
                    )
                continue

            signature.CropPath = str(destination)
            generated.append(destination)

    return generated


def _to_clip_rect(page, bbox: tuple[float, float, float, float]):
    width = float(page.rect.width)
    height = float(page.rect.height)

    x0, y0, x1, y1 = bbox
    left = _clamp(min(x0, x1), 0.0, width)
    right = _clamp(max(x0, x1), 0.0, width)

    top = _clamp(height - max(y0, y1), 0.0, height)
    bottom = _clamp(height - min(y0, y1), 0.0, height)

    if right - left <= 0 or bottom - top <= 0:
        return None
    return fitz.Rect(left, top, right, bottom)


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def _build_filename(index: int, signature: Signature) -> str:
    base = signature.Role or signature.FieldName or "signature"
    slug = _slugify(base)
    return f"sig_{index:02d}_{slug}.png"


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip().lower())
    cleaned = cleaned.strip("_")
    return cleaned or "signature"
