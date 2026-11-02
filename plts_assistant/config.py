"""Pembacaan konfigurasi aplikasi dari environment variable."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _as_int(name: str, default: int, minimum: int = 1) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} harus berupa bilangan bulat.") from exc
    if value < minimum:
        raise ValueError(f"Environment variable {name} minimal {minimum}.")
    return value


def _as_float(name: str, default: float, minimum: float = 0.0) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} harus berupa angka.") from exc
    if value < minimum:
        raise ValueError(f"Environment variable {name} minimal {minimum}.")
    return value


@dataclass(frozen=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    knowledge_base_dir: Path = PROJECT_ROOT / "knowledge_base"
    top_k: int = _as_int("RETRIEVAL_TOP_K", 4, 1)
    retrieval_threshold: float = _as_float("RETRIEVAL_THRESHOLD", 0.12, 0.0)
    chunk_size: int = _as_int("CHUNK_SIZE", 1100, 100)
    chunk_overlap: int = _as_int("CHUNK_OVERLAP", 160, 0)
    llm_api_key: str = os.getenv("LLM_API_KEY", "").strip()
    llm_base_url: str = os.getenv("LLM_BASE_URL", "").strip()
    llm_model: str = os.getenv("LLM_MODEL", "").strip()
    llm_timeout_seconds: int = _as_int("LLM_TIMEOUT_SECONDS", 45, 5)

    def __post_init__(self) -> None:
        if not 0.0 <= self.retrieval_threshold <= 1.0:
            raise ValueError("RETRIEVAL_THRESHOLD harus berada pada rentang 0 sampai 1.")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP harus lebih kecil daripada CHUNK_SIZE.")

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_api_key and self.llm_model)


settings = Settings()
