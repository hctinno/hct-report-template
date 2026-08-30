"""BM25 희소 검색.

한국어 질의는 임베딩만으로는 고유명사·코드·사번 같은 정확 일치를
자주 놓친다. 희소 검색을 함께 두는 이유다.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field

from .tokenize import tokenize


@dataclass
class BM25Index:
    """Okapi BM25. 문서 수가 수만 건 수준인 사내 코퍼스를 가정한다."""

    k1: float = 1.5
    b: float = 0.75
    doc_ids: list[str] = field(default_factory=list)
    _tf: list[Counter[str]] = field(default_factory=list, repr=False)
    _df: Counter[str] = field(default_factory=Counter, repr=False)
    _lengths: list[int] = field(default_factory=list, repr=False)

    @property
    def avg_length(self) -> float:
        return (sum(self._lengths) / len(self._lengths)) if self._lengths else 0.0

    def add(self, doc_id: str, text: str) -> None:
        """문서 하나를 색인에 넣는다."""
        tokens = tokenize(text)
        counts = Counter(tokens)
        self.doc_ids.append(doc_id)
        self._tf.append(counts)
        self._lengths.append(len(tokens))
        self._df.update(counts.keys())

    def add_many(self, items: list[tuple[str, str]]) -> None:
        for doc_id, text in items:
            self.add(doc_id, text)

    def _idf(self, term: str) -> float:
        n = len(self.doc_ids)
        df = self._df.get(term, 0)
        if df == 0:
            return 0.0
        return math.log(1.0 + (n - df + 0.5) / (df + 0.5))

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """질의어에 대한 (문서 id, 점수) 목록을 점수 내림차순으로 반환."""
        if not self.doc_ids:
            return []
        terms = Counter(tokenize(query))
        avg = self.avg_length or 1.0
        scored: list[tuple[str, float]] = []
        for i, doc_id in enumerate(self.doc_ids):
            tf = self._tf[i]
            length = self._lengths[i] or 1
            score = 0.0
            for term, q_count in terms.items():
                f = tf.get(term)
                if not f:
                    continue
                denom = f + self.k1 * (1 - self.b + self.b * length / avg)
                score += self._idf(term) * (f * (self.k1 + 1) / denom) * min(q_count, 3)
            if score > 0.0:
                scored.append((doc_id, score))
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        return scored[:top_k]

    def to_dict(self) -> dict[str, object]:
        return {
            "k1": self.k1,
            "b": self.b,
            "doc_ids": self.doc_ids,
            "tf": [dict(c) for c in self._tf],
            "lengths": self._lengths,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "BM25Index":
        index = cls(k1=float(data.get("k1", 1.5)), b=float(data.get("b", 0.75)))
        index.doc_ids = list(data.get("doc_ids", []))  # type: ignore[arg-type]
        index._tf = [Counter(d) for d in data.get("tf", [])]  # type: ignore[arg-type]
        index._lengths = list(data.get("lengths", []))  # type: ignore[arg-type]
        for counts in index._tf:
            index._df.update(counts.keys())
        return index
