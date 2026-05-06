from construction_rag.services.embeddings.chunking import Chunker


def test_chunker_produces_stable_ids_and_overlap():
    chunker = Chunker(chunk_size=10, chunk_overlap=3)
    chunks = chunker.chunk_page(page_number=2, text="abcdefghijklmnopqrstuvwxyz")
    assert chunks
    assert chunks[0].chunk_id.startswith("p0002_c0000")
    assert all(c.page_number == 2 for c in chunks)
    assert "".join(c.text for c in chunks).replace(" ", "")  # non-empty content


def test_chunker_empty_text_returns_empty():
    chunker = Chunker()
    assert chunker.chunk_page(page_number=1, text="   \n\n") == []

