import pytest

from app.ingestion.chunking.splitter import chunk_text


def test_chunk_text_keeps_chunks_within_limit():
    result = chunk_text("alpha\n\nbeta\n\ngamma", chunk_size=8)
    assert result == ["alpha", "beta", "gamma"]
    assert all(0 < len(chunk) <= 8 for chunk in result)


def test_chunk_text_splits_long_paragraph():
    result = chunk_text("abcdefghijk", chunk_size=4)
    assert result == ["abcd", "efgh", "ijk"]


def test_chunk_text_handles_empty_and_invalid_size():
    assert chunk_text(" \n\n ") == []
    with pytest.raises(ValueError):
        chunk_text("text", chunk_size=0)
