"""Schema keluaran untuk menjaga struktur jawaban aplikasi."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

AnswerStatus = Literal[
    "cukup_data",
    "data_belum_cukup",
    "informasi_tidak_ditemukan",
    "perlu_verifikasi",
]


class SourceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_chunk: str = Field(min_length=1)
    nama_file: str = Field(min_length=1)
    judul: str = Field(min_length=1)
    kutipan: str = Field(min_length=1)
    url: str | None = None
    skor_retrieval: float = Field(ge=0.0, le=1.0)


class AssistantAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AnswerStatus
    ringkasan: str = Field(min_length=1)
    hasil_perhitungan: dict[str, Any] | None = None
    temuan_dokumen: list[str] = Field(default_factory=list)
    sumber: list[SourceReference] = Field(default_factory=list)
    kemungkinan_penyebab: list[str] = Field(default_factory=list)
    pemeriksaan_lanjutan: list[str] = Field(default_factory=list)
    keterbatasan: list[str] = Field(default_factory=list)
