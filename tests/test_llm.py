import pytest

from plts_assistant.llm import LLMClient


def test_llm_json_parser_reads_fenced_json():
    result = LLMClient._extract_json('```json\n{"status":"perlu_verifikasi","ringkasan":"Perlu dicek."}\n```')
    assert result["status"] == "perlu_verifikasi"
    assert result["ringkasan"] == "Perlu dicek."


def test_llm_json_parser_rejects_non_json():
    with pytest.raises(ValueError):
        LLMClient._extract_json("Jawaban biasa tanpa JSON")
