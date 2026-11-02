from plts_assistant.documents import Chunk
from plts_assistant.retrieval import TfidfRetriever


def _chunk(chunk_id: str, doc_id: str, text: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        doc_id=doc_id,
        title=f"Dokumen {doc_id}",
        source_url=None,
        path=f"knowledge_base/{doc_id}.md",
        text=text,
    )


def test_tfidf_retrieves_expected_document():
    chunks = [
        _chunk("D1-C001", "D1", "Artificial intelligence is used for photovoltaic fault detection."),
        _chunk("D2-C001", "D2", "Battery energy storage scheduling and residential electricity profile."),
    ]
    retriever = TfidfRetriever(chunks)
    results = retriever.search("photovoltaic fault detection artificial intelligence", top_k=1, threshold=0.0)
    assert results
    assert results[0].chunk.doc_id == "D1"


def test_tfidf_rejects_empty_query():
    retriever = TfidfRetriever([_chunk("D1-C001", "D1", "photovoltaic performance ratio")])
    try:
        retriever.search("   ")
    except ValueError as exc:
        assert "kosong" in str(exc)
    else:
        raise AssertionError("Query kosong seharusnya ditolak.")


def test_unknown_equipment_identifier_is_not_matched_to_generic_text():
    chunks = [
        _chunk("D2-C001", "D2", "Reliability and predictive maintenance of grid-connected solar systems."),
    ]
    retriever = TfidfRetriever(chunks)
    results = retriever.search("Apa arti kode alarm A999 pada inverter?", top_k=4, threshold=0.0)
    assert results == []
