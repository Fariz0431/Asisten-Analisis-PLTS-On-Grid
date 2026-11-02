"""Alur retrieval, jawaban fallback, dan validasi rujukan."""

from __future__ import annotations

from typing import Any

from .config import Settings
from .documents import Chunk, build_chunks, load_documents
from .llm import LLMClient, LLMConfigurationError
from .retrieval import SearchResult, TfidfRetriever
from .schemas import AssistantAnswer, SourceReference


class AssistantEngine:
    def __init__(self, settings: Settings, use_llm: bool | None = None) -> None:
        self.settings = settings
        self.documents = load_documents(settings.knowledge_base_dir)
        self.chunks = build_chunks(
            self.documents,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )
        self.retriever = TfidfRetriever(self.chunks) if self.chunks else None
        self.llm_client: LLMClient | None = None
        should_use_llm = settings.llm_enabled if use_llm is None else use_llm
        if should_use_llm:
            try:
                self.llm_client = LLMClient(settings)
            except LLMConfigurationError:
                self.llm_client = None

    @staticmethod
    def _source_reference(result: SearchResult) -> SourceReference:
        chunk = result.chunk
        excerpt = chunk.text[:420].strip()
        return SourceReference(
            id_chunk=chunk.chunk_id,
            nama_file=chunk.path,
            judul=chunk.title,
            kutipan=excerpt,
            url=chunk.source_url,
            skor_retrieval=result.score,
        )

    def search(self, question: str, top_k: int | None = None, threshold: float | None = None) -> list[SearchResult]:
        if self.retriever is None:
            return []
        return self.retriever.search(
            question,
            top_k=top_k or self.settings.top_k,
            threshold=self.settings.retrieval_threshold if threshold is None else threshold,
        )

    def ask(
        self,
        question: str,
        calculation_result: dict[str, Any] | None = None,
        top_k: int | None = None,
        threshold: float | None = None,
    ) -> AssistantAnswer:
        if not question or not question.strip():
            raise ValueError("Pertanyaan tidak boleh kosong.")
        hits = self.search(question, top_k=top_k, threshold=threshold)
        sources = [self._source_reference(hit) for hit in hits]

        if not hits:
            answer = AssistantAnswer(
                status="informasi_tidak_ditemukan",
                ringkasan=(
                    "Belum ditemukan potongan dokumen yang melewati ambang retrieval. "
                    "Informasi yang diminta belum dapat dipastikan dari knowledge base saat ini."
                ),
                temuan_dokumen=[],
                sumber=[],
                pemeriksaan_lanjutan=[
                    "Periksa ejaan istilah, merek dan model peralatan, atau tambahkan dokumen teknis yang relevan.",
                    "Untuk analisis numerik, masukkan data dan satuan melalui kalkulator yang tersedia.",
                ],
                keterbatasan=["Skor retrieval tidak membuktikan bahwa suatu fakta benar atau salah."],
            )
            if calculation_result is not None:
                answer.hasil_perhitungan = calculation_result
                answer.status = "perlu_verifikasi"
            return answer

        if self.llm_client is None:
            answer = AssistantAnswer(
                status="perlu_verifikasi",
                ringkasan=(
                    "LLM belum aktif. Hasil di bawah merupakan potongan dokumen yang ditemukan oleh TF-IDF, "
                    "bukan jawaban generatif dan belum dinilai kecukupan buktinya."
                ),
                temuan_dokumen=[
                    f"{hit.chunk.chunk_id} (skor {hit.score:.4f}): {hit.chunk.text[:360].strip()}"
                    for hit in hits
                ],
                sumber=sources,
                pemeriksaan_lanjutan=[
                    "Buka sumber asli dan periksa apakah isinya benar-benar menjawab pertanyaan.",
                    "Aktifkan LLM hanya setelah provider dan kebijakan datanya diperiksa.",
                ],
                keterbatasan=[
                    "TF-IDF mengukur kemiripan leksikal, bukan kebenaran atau kecukupan bukti.",
                    "Mode retrieval-only tidak melakukan generasi jawaban dengan model bahasa.",
                ],
            )
            if calculation_result is not None:
                answer.hasil_perhitungan = calculation_result
            return answer

        context = [
            {
                "id_chunk": hit.chunk.chunk_id,
                "judul": hit.chunk.title,
                "teks": hit.chunk.text,
            }
            for hit in hits
        ]
        try:
            raw = self.llm_client.answer(question, context)
            cited_ids = raw.get("sumber", [])
            if isinstance(cited_ids, list):
                valid_ids = {source.id_chunk for source in sources}
                selected_sources = [source for source in sources if source.id_chunk in set(cited_ids) & valid_ids]
            else:
                selected_sources = []
            raw["sumber"] = [source.model_dump() for source in selected_sources]
            raw.setdefault("temuan_dokumen", [])
            raw.setdefault("kemungkinan_penyebab", [])
            raw.setdefault("pemeriksaan_lanjutan", [])
            raw.setdefault("keterbatasan", [])
            raw["hasil_perhitungan"] = calculation_result
            answer = AssistantAnswer.model_validate(raw)
            if not answer.sumber:
                answer.status = "perlu_verifikasi"
                answer.keterbatasan.append("Model tidak mengembalikan ID sumber valid dari hasil retrieval.")
            if calculation_result is not None:
                answer.hasil_perhitungan = calculation_result
            return answer
        except Exception as exc:
            fallback = AssistantAnswer(
                status="perlu_verifikasi",
                ringkasan=(
                    "Generasi jawaban tidak berhasil divalidasi. Potongan retrieval ditampilkan agar sumber "
                    "dapat diperiksa secara manual; jawaban model tidak digunakan."
                ),
                temuan_dokumen=[hit.chunk.text[:360].strip() for hit in hits],
                sumber=sources,
                pemeriksaan_lanjutan=["Periksa log aplikasi dan buka dokumen sumber sebelum menarik kesimpulan."],
                keterbatasan=[f"Validasi/pemanggilan LLM gagal: {type(exc).__name__}."],
                hasil_perhitungan=calculation_result,
            )
            return fallback
