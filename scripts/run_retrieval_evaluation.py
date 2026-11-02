"""Jalankan evaluasi retrieval pada sepuluh pertanyaan uji yang disediakan."""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from plts_assistant.config import settings  # noqa: E402
from plts_assistant.documents import build_chunks, load_documents  # noqa: E402
from plts_assistant.retrieval import TfidfRetriever  # noqa: E402


def main() -> int:
    case_path = ROOT / "tests" / "test_cases.json"
    cases = json.loads(case_path.read_text(encoding="utf-8"))
    documents = load_documents(settings.knowledge_base_dir)
    chunks = build_chunks(documents, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        raise SystemExit("Knowledge base tidak memiliki teks yang dapat diindeks.")
    retriever = TfidfRetriever(chunks)

    records: list[dict] = []
    for case in cases:
        results = retriever.search(
            case["question"],
            top_k=settings.top_k,
            threshold=settings.retrieval_threshold,
        )
        retrieved_doc_ids = list(dict.fromkeys(item.chunk.doc_id for item in results))
        expected = set(case["expected_doc_ids"])
        found_targets = expected.intersection(retrieved_doc_ids)
        target_hit = (expected.issubset(set(retrieved_doc_ids))) if expected else None
        target_coverage = (len(found_targets) / len(expected)) if expected else None
        records.append(
            {
                "id": case["id"],
                "category": case["category"],
                "question": case["question"],
                "expected_doc_ids": ";".join(case["expected_doc_ids"]),
                "retrieved_doc_ids": ";".join(retrieved_doc_ids),
                "retrieved_chunk_ids": ";".join(item.chunk.chunk_id for item in results),
                "scores": ";".join(f"{item.score:.4f}" for item in results),
                "top_score": round(results[0].score, 6) if results else 0.0,
                "result_count": len(results),
                "target_hit_all_expected": target_hit,
                "target_source_coverage": round(target_coverage, 4) if target_coverage is not None else None,
                "negative_query_has_result": bool(results) if case["expect_no_hit"] else None,
            }
        )

    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)
    csv_path = output_dir / "retrieval_evaluation.csv"
    json_path = output_dir / "retrieval_evaluation.json"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "backend": "TF-IDF cosine similarity",
        "top_k": settings.top_k,
        "threshold": settings.retrieval_threshold,
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "records": records,
        "note": "Retrieval evaluation only; does not assess generative answer correctness or field diagnosis.",
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    positive = [r for r in records if r["category"] in {"single_source", "cross_document", "negative_context"}]
    hits = [r for r in positive if r["target_hit_all_expected"]]
    negative = [r for r in records if r["category"] == "negative"]
    negative_with_results = [r for r in negative if r["negative_query_has_result"]]
    print(f"Dokumen: {len(documents)} | Chunk: {len(chunks)} | Pertanyaan: {len(records)}")
    print(f"Cakupan seluruh sumber target (single/cross/negative-context): {len(hits)}/{len(positive)}")
    print(f"Pertanyaan negatif yang tetap mendapat hasil (kandidat false positive): {len(negative_with_results)}/{len(negative)}")
    print("Q10 adalah pertanyaan nilai aktual yang tidak tersedia; konteks umum D5/D8 boleh muncul untuk mendukung penjelasan bahwa nilainya tidak dapat ditentukan.")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    print("Periksa isi setiap hasil secara manual; skor retrieval bukan bukti kecukupan sumber.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
