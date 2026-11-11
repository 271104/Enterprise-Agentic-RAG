import pytest

from app.ingestion import processor


def test_processed_filename_cannot_escape_output_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(processor, "PROCESSED_DATA_DIR", str(tmp_path))
    with pytest.raises(ValueError):
        processor.save_processed_locally({}, "../escape", "doc.txt")


def test_ingestion_detects_embedding_count_mismatch(monkeypatch, tmp_path):
    monkeypatch.setattr(processor, "PROCESSED_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(processor, "parse_text", lambda _: "some source text")
    monkeypatch.setattr(processor, "chunk_text", lambda _: ["one", "two"])
    monkeypatch.setattr(processor, "embed_texts", lambda _: [[0.1]])
    result = processor.process_file("source.txt", "source.txt", "true")
    assert result is False
