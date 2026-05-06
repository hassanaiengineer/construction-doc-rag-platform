from __future__ import annotations

from functools import lru_cache
from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=4)
def _load_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


class Embedder:
    def __init__(self, model_name: str):
        self._model_name = model_name

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_texts(self, texts: Iterable[str]) -> np.ndarray:
        model = _load_model(self._model_name)
        embeddings = model.encode(list(texts), normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(embeddings, dtype=np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        vec = self.embed_texts([text])
        return vec[0]

