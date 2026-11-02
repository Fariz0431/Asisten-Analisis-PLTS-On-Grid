"""Baseline retrieval leksikal menggunakan TF-IDF dan cosine similarity."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .documents import Chunk


@dataclass(frozen=True)
class SearchResult:
    chunk: Chunk
    score: float


class TfidfRetriever:
    def __init__(self, chunks: Sequence[Chunk]) -> None:
        if not chunks:
            raise ValueError("Retriever tidak dapat dibuat tanpa chunk dokumen.")
        self.chunks = list(chunks)
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=50000,
            token_pattern=r"(?u)\b\w\w+\b",
        )
        corpus = [chunk.text for chunk in self.chunks]
        self.matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 4, threshold: float = 0.12) -> list[SearchResult]:
        if not query or not query.strip():
            raise ValueError("Pertanyaan tidak boleh kosong.")
        if top_k < 1:
            raise ValueError("top_k minimal 1.")
        if not 0 <= threshold <= 1:
            raise ValueError("threshold harus berada pada rentang 0 sampai 1.")

        # Kode/model seperti A999 tidak boleh dijawab dari artikel gangguan umum.
        # Jika query memuat identifier alfanumerik, identifier itu harus muncul persis
        # pada setidaknya satu chunk sebelum kandidat retrieval dikembalikan.
        identifiers = re.findall(r"\b[A-Z]{1,5}[-_]?\d{2,6}\b", query.upper())
        corpus_text = "\n".join(chunk.text.upper() for chunk in self.chunks)
        if identifiers and any(identifier not in corpus_text for identifier in identifiers):
            return []

        query_vector = self.vectorizer.transform([query.strip()])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        ranked_indices = scores.argsort()[::-1]
        results: list[SearchResult] = []
        for index in ranked_indices:
            score = float(scores[index])
            if score < threshold:
                continue
            results.append(SearchResult(chunk=self.chunks[int(index)], score=score))
            if len(results) >= top_k:
                break
        return results
