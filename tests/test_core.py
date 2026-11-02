import pytest

from plts_assistant.calculator import (
    calculate_cuf,
    calculate_energy_difference,
    calculate_performance_ratio,
)
from plts_assistant.documents import chunk_text
from plts_assistant.schemas import AssistantAnswer


def test_performance_ratio_known_values():
    result = calculate_performance_ratio(energy_grid_kwh=900, glob_inc_kwh_m2=150, installed_power_kwp=10)
    assert result["nilai"] == pytest.approx(0.6)
    assert result["persen"] == pytest.approx(60.0)


def test_cuf_known_values():
    result = calculate_cuf(energy_kwh=720, installed_power_kw=10, period_hours=720)
    assert result["persen"] == pytest.approx(10.0)


def test_energy_difference():
    result = calculate_energy_difference(actual_energy_kwh=900, reference_energy_kwh=1000)
    assert result["selisih_kwh"] == pytest.approx(-100)
    assert result["persentase_terhadap_referensi"] == pytest.approx(-10)


def test_energy_difference_reference_zero():
    result = calculate_energy_difference(actual_energy_kwh=5, reference_energy_kwh=0)
    assert result["persentase_terhadap_referensi"] is None


@pytest.mark.parametrize(
    "args",
    [
        (1, 0, 1),
        (1, 1, 0),
        (-1, 1, 1),
        (float("nan"), 1, 1),
    ],
)
def test_pr_rejects_invalid_inputs(args):
    with pytest.raises(ValueError):
        calculate_performance_ratio(*args)


def test_cuf_rejects_zero_hours():
    with pytest.raises(ValueError):
        calculate_cuf(100, 10, 0)


def test_chunk_text_respects_limit_and_overlap():
    text = "kata " * 900
    chunks = chunk_text(text, chunk_size=300, overlap=50)
    assert len(chunks) > 1
    assert all(len(chunk) <= 300 for chunk in chunks)
    assert all(chunk.strip() for chunk in chunks)


def test_answer_schema_accepts_allowed_status():
    answer = AssistantAnswer(status="perlu_verifikasi", ringkasan="Sumber perlu diperiksa.")
    assert answer.status == "perlu_verifikasi"


def test_answer_schema_rejects_unknown_status():
    with pytest.raises(ValueError):
        AssistantAnswer(status="verified", ringkasan="Status tidak dikenal.")
