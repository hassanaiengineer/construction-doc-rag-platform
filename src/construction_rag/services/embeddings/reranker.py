from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from sentence_transformers import CrossEncoder


@dataclass(frozen=True, slots=True)
class RerankedItem:
    index: int
    score: float


@lru_cache(maxsize=2)
def _load_cross_encoder(model_name: str) -> CrossEncoder:
    return CrossEncoder(model_name)


class Reranker:
    def __init__(self, model_name: str):
        self._model_name = model_name

    def rerank(self, *, query: str, passages: list[str]) -> list[RerankedItem]:
        model = _load_cross_encoder(self._model_name)
        scores = model.predict([(query, p) for p in passages], show_progress_bar=False)
        return sorted(
            (RerankedItem(index=i, score=float(s)) for i, s in enumerate(scores)),
            key=lambda x: x.score,
            reverse=True,
        )

