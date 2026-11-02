from dataclasses import replace
from pathlib import Path

from plts_assistant.config import settings
from plts_assistant.pipeline import AssistantEngine


def test_engine_fallback_uses_only_retrieved_sources():
    temp_kb = Path(__file__).resolve().parents[1] / "knowledge_base"
    test_settings = replace(settings, knowledge_base_dir=temp_kb, retrieval_threshold=0.0)
    engine = AssistantEngine(test_settings, use_llm=False)
    answer = engine.ask("Apa definisi Performance Ratio pada dokumentasi PVsyst?")
    assert answer.status == "perlu_verifikasi"
    assert answer.sumber
    indexed_ids = {chunk.chunk_id for chunk in engine.chunks}
    assert all(source.id_chunk in indexed_ids for source in answer.sumber)
    assert "bukan jawaban generatif" in answer.ringkasan


def test_engine_returns_not_found_for_unrelated_query():
    test_settings = replace(settings, retrieval_threshold=1.0)
    engine = AssistantEngine(test_settings, use_llm=False)
    answer = engine.ask("informasi yang tidak berhubungan sama sekali xyzqv 987654")
    assert answer.status == "informasi_tidak_ditemukan"
    assert answer.sumber == []


def test_repository_knowledge_base_has_eight_indexed_sources():
    project_root = Path(__file__).resolve().parents[1]
    test_settings = replace(settings, knowledge_base_dir=project_root / "knowledge_base")
    engine = AssistantEngine(test_settings, use_llm=False)
    assert len(engine.documents) == 8
    assert {document.doc_id for document in engine.documents} == {f"D{i}" for i in range(1, 9)}
