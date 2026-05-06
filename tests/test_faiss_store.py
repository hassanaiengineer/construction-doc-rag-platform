from pathlib import Path

import numpy as np

from construction_rag.services.embeddings.chunking import Chunk
from construction_rag.services.embeddings.faiss_store import FaissVectorStore


def test_faiss_store_build_and_search(tmp_path: Path):
    index_dir = tmp_path / "idx"
    store = FaissVectorStore(index_dir)

    chunks = [
        Chunk(chunk_id="c1", page_number=1, text="steel beam schedule"),
        Chunk(chunk_id="c2", page_number=2, text="concrete slab thickness"),
    ]
    # 2 vectors, dim=3, already normalized for IP search
    embeddings = np.array([[1, 0, 0], [0, 1, 0]], dtype=np.float32)
    store.build(embeddings=embeddings, chunks=chunks)

    results = store.search(query_embedding=np.array([1, 0, 0], dtype=np.float32), top_k=2)
    assert results
    assert results[0].chunk_id == "c1"
    assert results[0].page_number == 1

