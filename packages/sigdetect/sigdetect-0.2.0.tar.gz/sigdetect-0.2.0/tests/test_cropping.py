from pathlib import Path

import pytest
from pypdf import PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, NumberObject, TextStringObject

from sigdetect.api import CropSignatureImages, DetectPdf
from sigdetect.config import DetectConfiguration
from sigdetect.cropping import crop_signatures
from sigdetect.detector.pypdf2_engine import PyPDF2Detector

pytest.importorskip("fitz")


def _pdf_with_signature(path: Path) -> None:
    writer = PdfWriter()
    page = writer.add_blank_page(300, 300)

    field = DictionaryObject()
    field.update({NameObject("/FT"): NameObject("/Sig"), NameObject("/T"): TextStringObject("sig")})
    field_ref = writer._add_object(field)

    widget = DictionaryObject()
    widget.update(
        {
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Widget"),
            NameObject("/Rect"): ArrayObject(
                [NumberObject(50), NumberObject(50), NumberObject(200), NumberObject(120)]
            ),
            NameObject("/Parent"): field_ref,
        }
    )
    widget_ref = writer._add_object(widget)
    field.update({NameObject("/Kids"): ArrayObject([widget_ref])})

    page[NameObject("/Annots")] = ArrayObject([widget_ref])
    acro = DictionaryObject()
    acro.update({NameObject("/Fields"): ArrayObject([field_ref])})
    writer._root_object.update({NameObject("/AcroForm"): acro})

    with open(path, "wb") as handle:
        writer.write(handle)


def test_crop_signatures(tmp_path: Path):
    pdf_path = tmp_path / "doc.pdf"
    _pdf_with_signature(pdf_path)

    cfg = DetectConfiguration(pdf_root=tmp_path, out_dir=tmp_path, engine="pypdf2")
    result = PyPDF2Detector(cfg).Detect(pdf_path)

    out_dir = tmp_path / "crops"
    generated = crop_signatures(pdf_path, result, output_dir=out_dir, dpi=120)

    assert generated, "Expected at least one cropped image"
    for sig in result.Signatures:
        if sig.BoundingBox:
            assert sig.CropPath is not None
            assert Path(sig.CropPath).exists()


def test_crop_signature_images_accepts_dict(tmp_path: Path) -> None:
    pdf_path = tmp_path / "doc.pdf"
    _pdf_with_signature(pdf_path)

    result_dict = DetectPdf(pdf_path, engineName="pymupdf")
    out_dir = tmp_path / "dict_crops"
    paths = CropSignatureImages(pdf_path, result_dict, outputDirectory=out_dir)

    assert paths
    assert result_dict["signatures"][0]["crop_path"] is not None
