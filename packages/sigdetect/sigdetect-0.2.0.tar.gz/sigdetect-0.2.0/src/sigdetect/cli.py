"""Command line interface for the signature detection tool."""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import asdict, is_dataclass
from pathlib import Path

import typer

from . import __version__
from .config import FinalizeConfiguration, LoadConfiguration
from .cropping import SignatureCroppingUnavailable, crop_signatures
from .detector import BuildDetector, FileResult
from .eda import RunExploratoryAnalysis
from .logging_setup import ConfigureLogging

Logger = ConfigureLogging()

CliApplication = typer.Typer(help="Signature detection & role attribution for PDFs")


def _JsonSerializer(candidate):
    """Ensure dataclasses and paths remain JSON serialisable."""

    if hasattr(candidate, "to_dict"):
        return candidate.to_dict()
    if is_dataclass(candidate):
        return asdict(candidate)
    if isinstance(candidate, Path):
        return str(candidate)
    return str(candidate)


def _EnumeratePdfs(pdfRoot: Path, recursive: bool) -> Iterator[Path]:
    """Yield PDF files under ``pdfRoot`` honoring the recursion flag."""

    iterator = pdfRoot.rglob("*") if recursive else pdfRoot.glob("*")
    for path in iterator:
        if path.is_file() and path.suffix.lower() == ".pdf":
            yield path


@CliApplication.command(name="detect")
def Detect(
    configurationPath: Path | None = typer.Option(
        None, "--config", "-c", help="Path to YAML config"
    ),
    profileOverride: str | None = typer.Option(None, "--profile", "-p", help="hipaa or retainer"),
    recursive: bool = typer.Option(
        True,
        "--recursive/--no-recursive",
        help="Recurse into subdirectories when gathering PDFs",
    ),
    cropSignatures: bool | None = typer.Option(
        None,
        "--crop-signatures/--no-crop-signatures",
        help="Crop detected signature regions to PNG files (requires PyMuPDF)",
        show_default=False,
    ),
    cropDirectory: Path | None = typer.Option(
        None,
        "--crop-dir",
        help="Directory for signature PNG crops (defaults to out_dir/signature_crops)",
    ),
    cropDpi: int | None = typer.Option(
        None,
        "--crop-dpi",
        min=72,
        max=600,
        help="Rendering DPI for signature crops",
        show_default=False,
    ),
) -> None:
    """Run detection for the configured directory and emit ``results.json``."""

    configuration = LoadConfiguration(configurationPath)
    if profileOverride is not None:
        normalized_profile = profileOverride.lower()
        if normalized_profile not in {"hipaa", "retainer"}:
            raise typer.BadParameter("Profile must be 'hipaa' or 'retainer'.")
        configuration = configuration.model_copy(update={"Profile": normalized_profile})

    overrides: dict[str, object] = {}
    if cropSignatures is not None:
        overrides["CropSignatures"] = cropSignatures
    if cropDirectory is not None:
        overrides["CropOutputDirectory"] = cropDirectory
    if cropDpi is not None:
        overrides["CropImageDpi"] = cropDpi
    if overrides:
        configuration = configuration.model_copy(update=overrides)
        configuration = FinalizeConfiguration(configuration)

    try:
        detector = BuildDetector(configuration)
    except ValueError as exc:
        Logger.error(
            "Detector initialisation failed",
            extra={"engine": configuration.Engine, "error": str(exc)},
        )
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc

    pdfIterator = _EnumeratePdfs(configuration.PdfRoot, recursive)
    try:
        firstPdf = next(pdfIterator)
    except StopIteration:
        raise SystemExit(f"No PDFs found in {configuration.PdfRoot}") from None

    results_buffer: list[FileResult] | None = [] if configuration.OutputDirectory is None else None
    json_handle = None
    json_path: Path | None = None
    wrote_first = False

    if configuration.OutputDirectory is not None:
        outputDirectory = configuration.OutputDirectory
        outputDirectory.mkdir(parents=True, exist_ok=True)
        json_path = outputDirectory / "results.json"
        json_handle = open(json_path, "w", encoding="utf-8")
        json_handle.write("[")

    crop_dir = configuration.CropOutputDirectory
    cropping_enabled = configuration.CropSignatures
    cropping_available = True
    cropping_attempted = False
    if configuration.CropSignatures and crop_dir is None:
        Logger.warning(
            "CropSignatures enabled without an output directory",
            extra={"pdf_root": str(configuration.PdfRoot)},
        )
        cropping_enabled = False

    total_bboxes = 0

    def _append_result(file_result: FileResult, source_pdf: Path) -> None:
        nonlocal wrote_first, json_handle, total_bboxes, cropping_available, cropping_attempted

        if cropping_enabled and cropping_available and crop_dir is not None:
            try:
                crop_signatures(
                    pdf_path=source_pdf,
                    file_result=file_result,
                    output_dir=crop_dir,
                    dpi=configuration.CropImageDpi,
                    logger=Logger,
                )
                cropping_attempted = True
            except SignatureCroppingUnavailable as exc:
                cropping_available = False
                Logger.warning("Signature cropping unavailable", extra={"error": str(exc)})
                typer.echo(str(exc), err=True)
            except Exception as exc:  # pragma: no cover - defensive
                Logger.warning(
                    "Unexpected error while cropping signatures",
                    extra={"error": str(exc)},
                )

        total_bboxes += sum(1 for sig in file_result.Signatures if sig.BoundingBox)

        if results_buffer is not None:
            results_buffer.append(file_result)
            return

        if json_handle is None:
            return

        serialized = json.dumps(
            file_result,
            indent=2,
            ensure_ascii=False,
            default=_JsonSerializer,
        )
        indented = "\n".join(f"  {line}" for line in serialized.splitlines())
        if wrote_first:
            json_handle.write(",\n")
        else:
            json_handle.write("\n")
        json_handle.write(indented)
        wrote_first = True

    def _process(pdf_path: Path) -> None:
        file_result = detector.Detect(pdf_path)
        _append_result(file_result, pdf_path)

    try:
        _process(firstPdf)
        for pdf_path in pdfIterator:
            _process(pdf_path)
    finally:
        if json_handle is not None:
            closing = "\n]\n" if wrote_first else "]\n"
            json_handle.write(closing)
            json_handle.close()

    if json_handle is not None:
        typer.echo(f"Wrote {json_path}")
    else:
        payload = json.dumps(
            results_buffer or [], indent=2, ensure_ascii=False, default=_JsonSerializer
        )
        typer.echo(payload)
        typer.echo("Detection completed with output disabled (out_dir=none)")

    if cropping_enabled and cropping_available and cropping_attempted and total_bboxes == 0:
        Logger.warning(
            "No signature bounding boxes detected; try --engine pymupdf for crop-ready output",
            extra={"engine": configuration.Engine},
        )


@CliApplication.command(name="eda")
def ExploratoryAnalysis(
    configurationPath: Path | None = typer.Option(
        None, "--config", "-c", help="Path to YAML config"
    ),
) -> None:
    """Generate a compact exploratory summary for the dataset."""

    configuration = LoadConfiguration(configurationPath)
    RunExploratoryAnalysis(configuration)


@CliApplication.command(name="version")
def Version() -> None:
    """Print the installed package version."""

    typer.echo(__version__)


app = CliApplication
