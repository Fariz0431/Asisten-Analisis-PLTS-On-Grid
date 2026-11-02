"""Pemuatan dokumen dan pemotongan teks menjadi chunk."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf"}


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    source_url: str | None
    path: str
    text: str


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    source_url: str | None
    path: str
    text: str


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - dependency installed from requirements
        raise RuntimeError("Dependensi pypdf belum terpasang. Jalankan pip install -r requirements.txt.") from exc

    reader = PdfReader(str(path))
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(f"[Halaman {index}]\n{page_text}")
    return "\n\n".join(pages)


def _extract_metadata(path: Path, text: str) -> tuple[str, str, str | None]:
    doc_match = re.search(r"(?im)^DOC_ID:\s*(.+?)\s*$", text)
    title_match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    url_match = re.search(r"(?im)^(?:SOURCE_URL|URL|Sumber URL):\s*(https?://\S+)\s*$", text)
    doc_id = doc_match.group(1).strip() if doc_match else path.stem.upper()
    title = title_match.group(1).strip() if title_match else path.stem.replace("_", " ").replace("-", " ")
    source_url = url_match.group(1).strip() if url_match else None
    return doc_id, title, source_url


def load_documents(directory: Path) -> list[Document]:
    """Muat file Markdown, TXT, dan PDF yang memiliki teks terbaca."""
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Direktori knowledge base tidak ditemukan: {directory}")

    documents: list[Document] = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if path.name.lower() == "readme.md":
            continue
        try:
            text = _read_pdf(path) if path.suffix.lower() == ".pdf" else path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise RuntimeError(f"Gagal membaca dokumen {path}: {exc}") from exc
        if not text.strip():
            continue
        doc_id, title, source_url = _extract_metadata(path, text)
        documents.append(
            Document(
                doc_id=doc_id,
                title=title,
                source_url=source_url,
                path=str(path.relative_to(directory.parent)),
                text=text.strip(),
            )
        )
    return documents


def chunk_text(text: str, chunk_size: int = 1100, overlap: int = 160) -> list[str]:
    """Potong teks berdasarkan karakter dengan overlap dan batas kata sederhana."""
    if chunk_size < 100:
        raise ValueError("chunk_size minimal 100 karakter.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap harus >= 0 dan lebih kecil daripada chunk_size.")

    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    start = 0
    text_length = len(normalized)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        if end < text_length:
            boundary = normalized.rfind(" ", start + chunk_size // 2, end)
            if boundary > start:
                end = boundary
        piece = normalized[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= text_length:
            break
        next_start = max(end - overlap, start + 1)
        start = next_start
    return chunks


def build_chunks(
    documents: Iterable[Document], chunk_size: int = 1100, overlap: int = 160
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        pieces = chunk_text(document.text, chunk_size=chunk_size, overlap=overlap)
        for index, piece in enumerate(pieces, start=1):
            chunks.append(
                Chunk(
                    chunk_id=f"{document.doc_id}-C{index:03d}",
                    doc_id=document.doc_id,
                    title=document.title,
                    source_url=document.source_url,
                    path=document.path,
                    text=piece,
                )
            )
    return chunks
