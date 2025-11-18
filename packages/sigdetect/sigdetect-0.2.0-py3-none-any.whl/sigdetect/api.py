"""Public helpers for programmatic use of the signature detection engine."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Iterable, Iterator, Literal

from sigdetect.config import DetectConfiguration
from sigdetect.detector import BuildDetector, Detector, FileResult, Signature

EngineName = Literal["pypdf2", "pypdf", "pymupdf"]
ProfileName = Literal["hipaa", "retainer"]


def DetectPdf(
    pdfPath: str | Path,
    *,
    profileName: ProfileName = "hipaa",
    engineName: EngineName = "pypdf2",
    includePseudoSignatures: bool = True,
    recurseXObjects: bool = True,
    detector: Detector | None = None,
) -> dict[str, Any]:
    """Detect signature evidence and assign roles for a single PDF."""

    resolvedPath = Path(pdfPath)
    activeDetector = detector or get_detector(
        pdfRoot=resolvedPath.parent,
        profileName=profileName,
        engineName=engineName,
        includePseudoSignatures=includePseudoSignatures,
        recurseXObjects=recurseXObjects,
        outputDirectory=None,
    )

    result = activeDetector.Detect(resolvedPath)
    return _ToPlainDictionary(result)


def get_detector(
    *,
    pdfRoot: str | Path | None = None,
    profileName: ProfileName = "hipaa",
    engineName: EngineName = "pypdf2",
    includePseudoSignatures: bool = True,
    recurseXObjects: bool = True,
    outputDirectory: str | Path | None = None,
) -> Detector:
    """Return a reusable detector instance configured with the supplied options."""

    configuration = DetectConfiguration(
        PdfRoot=Path(pdfRoot) if pdfRoot is not None else Path.cwd(),
        OutputDirectory=Path(outputDirectory) if outputDirectory is not None else None,
        Engine=engineName,
        PseudoSignatures=includePseudoSignatures,
        RecurseXObjects=recurseXObjects,
        Profile=profileName,
    )
    return BuildDetector(configuration)


def _ToPlainDictionary(candidate: Any) -> dict[str, Any]:
    """Convert pydantic/dataclass instances to plain dictionaries."""

    if hasattr(candidate, "to_dict"):
        return candidate.to_dict()
    if hasattr(candidate, "model_dump"):
        return candidate.model_dump()  # type: ignore[attr-defined]
    if hasattr(candidate, "dict"):
        return candidate.dict()  # type: ignore[attr-defined]
    try:
        from dataclasses import asdict, is_dataclass

        if is_dataclass(candidate):
            return asdict(candidate)
    except Exception:
        pass
    if isinstance(candidate, dict):
        return {key: _ToPlainValue(candidate[key]) for key in candidate}
    raise TypeError(f"Unsupported result type: {type(candidate)!r}")


def _ToPlainValue(value: Any) -> Any:
    """Best effort conversion for nested structures."""

    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "model_dump") or hasattr(value, "dict"):
        return _ToPlainDictionary(value)
    try:
        from dataclasses import asdict, is_dataclass

        if is_dataclass(value):
            return asdict(value)
    except Exception:
        pass
    if isinstance(value, list):
        return [_ToPlainValue(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_ToPlainValue(item) for item in value)
    if isinstance(value, dict):
        return {key: _ToPlainValue(result) for key, result in value.items()}
    return value


def DetectMany(
    pdfPaths: Iterable[str | Path],
    *,
    detector: Detector | None = None,
    **kwargs: Any,
) -> Iterator[dict[str, Any]]:
    """Yield :func:`DetectPdf` results for each path in ``pdfPaths``."""

    if detector is not None:
        for pdfPath in pdfPaths:
            yield _DetectWithDetector(detector, pdfPath)
        return

    for pdfPath in pdfPaths:
        yield DetectPdf(pdfPath, **kwargs)


def ScanDirectory(
    pdfRoot: str | Path,
    *,
    globPattern: str = "**/*.pdf",
    detector: Detector | None = None,
    **kwargs: Any,
) -> Iterator[dict[str, Any]]:
    """Walk ``pdfRoot`` and yield detection output for every matching PDF."""

    rootDirectory = Path(pdfRoot)
    if globPattern == "**/*.pdf":
        iterator = (path for path in rootDirectory.rglob("*") if path.is_file())
    else:
        iterator = (
            rootDirectory.rglob(globPattern.replace("**/", "", 1))
            if globPattern.startswith("**/")
            else rootDirectory.glob(globPattern)
        )

    for pdfPath in iterator:
        if pdfPath.is_file() and pdfPath.suffix.lower() == ".pdf":
            yield DetectPdf(pdfPath, detector=detector, **kwargs)


def ToCsvRow(result: dict[str, Any]) -> dict[str, Any]:
    """Return a curated subset of keys suitable for CSV export."""

    return {
        "file": result.get("file"),
        "size_kb": result.get("size_kb"),
        "pages": result.get("pages"),
        "esign_found": result.get("esign_found"),
        "scanned_pdf": result.get("scanned_pdf"),
        "mixed": result.get("mixed"),
        "sig_count": result.get("sig_count"),
        "sig_pages": result.get("sig_pages"),
        "roles": result.get("roles"),
        "hints": result.get("hints"),
    }


def Version() -> str:
    """Expose the installed package version without importing the CLI stack."""

    try:
        from importlib.metadata import version as resolveVersion

        return resolveVersion("sigdetect")
    except Exception:
        return "0.0.0-dev"


def _DetectWithDetector(detector: Detector, pdfPath: str | Path) -> dict[str, Any]:
    """Helper that runs ``detector`` and returns the plain dictionary result."""

    resolvedPath = Path(pdfPath)
    return _ToPlainDictionary(detector.Detect(resolvedPath))


@contextmanager
def detector_context(**kwargs: Any) -> Generator[Detector, None, None]:
    """Context manager wrapper around :func:`get_detector`."""

    detector = get_detector(**kwargs)
    try:
        yield detector
    finally:
        pass


def CropSignatureImages(
    pdfPath: str | Path,
    fileResult: FileResult | dict[str, Any],
    *,
    outputDirectory: str | Path,
    dpi: int = 200,
) -> list[Path]:
    """Crop detected signature regions to PNG files.

    Accepts either a :class:`FileResult` instance or the ``dict`` returned by
    :func:`DetectPdf`. Requires the optional ``pymupdf`` dependency.
    """

    from sigdetect.cropping import crop_signatures

    file_result_obj, original_dict = _CoerceFileResult(fileResult)
    paths = crop_signatures(
        pdf_path=Path(pdfPath),
        file_result=file_result_obj,
        output_dir=Path(outputDirectory),
        dpi=dpi,
    )
    if original_dict is not None:
        original_dict.clear()
        original_dict.update(file_result_obj.to_dict())
    return paths


def _CoerceFileResult(
    candidate: FileResult | dict[str, Any]
) -> tuple[FileResult, dict[str, Any] | None]:
    if isinstance(candidate, FileResult):
        return candidate, None
    if not isinstance(candidate, dict):
        raise TypeError("fileResult must be FileResult or dict")

    signatures: list[Signature] = []
    for entry in candidate.get("signatures") or []:
        bbox = entry.get("bounding_box")
        signatures.append(
            Signature(
                Page=entry.get("page"),
                FieldName=str(entry.get("field_name") or ""),
                Role=str(entry.get("role") or "unknown"),
                Score=int(entry.get("score") or 0),
                Scores=dict(entry.get("scores") or {}),
                Evidence=list(entry.get("evidence") or []),
                Hint=str(entry.get("hint") or ""),
                RenderType=str(entry.get("render_type") or "unknown"),
                BoundingBox=tuple(bbox) if bbox else None,
                CropPath=entry.get("crop_path"),
            )
        )

    file_result = FileResult(
        File=str(candidate.get("file") or ""),
        SizeKilobytes=candidate.get("size_kb"),
        PageCount=int(candidate.get("pages") or 0),
        ElectronicSignatureFound=bool(candidate.get("esign_found")),
        ScannedPdf=candidate.get("scanned_pdf"),
        MixedContent=candidate.get("mixed"),
        SignatureCount=int(candidate.get("sig_count") or len(signatures)),
        SignaturePages=str(candidate.get("sig_pages") or ""),
        Roles=str(candidate.get("roles") or "unknown"),
        Hints=str(candidate.get("hints") or ""),
        Signatures=signatures,
    )
    return file_result, candidate
