from app.ingestion.loaders.html import parse_html
from app.ingestion.loaders import office, pdf
from app.ingestion.loaders.text import parse_text


def test_text_loader_reads_utf8(tmp_path):
    source = tmp_path / "sample.txt"
    source.write_text("café", encoding="utf-8")
    assert parse_text(str(source)) == "café"


def test_html_loader_removes_script_and_style(tmp_path):
    source = tmp_path / "sample.html"
    source.write_text(
        "<html><body><h1>Useful</h1><script>secret()</script>"
        "<style>.x{}</style></body></html>",
        encoding="utf-8",
    )
    result = parse_html(str(source))
    assert "Useful" in result
    assert "secret" not in result
    assert ".x" not in result


def test_pdf_loader_extracts_pages(monkeypatch):
    class FakeReader:
        pages = [type("Page", (), {"extract_text": lambda self: "page one"})()]

    monkeypatch.setattr(pdf, "PdfReader", lambda _path: FakeReader())
    assert pdf.parse_pdf("sample.pdf") == "page one"


def test_office_loader_joins_elements(monkeypatch):
    monkeypatch.setattr(office, "partition", lambda **_: ["first", "second"])
    assert office.parse_office("sample.docx") == "first\nsecond"
