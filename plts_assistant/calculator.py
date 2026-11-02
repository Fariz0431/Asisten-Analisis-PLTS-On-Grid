"""Kalkulator PLTS deterministik; tidak digunakan untuk diagnosis gangguan."""

from __future__ import annotations

import math


def _positive_finite(name: str, value: float, *, allow_zero: bool = False) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} harus berupa angka.") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} harus bernilai hingga (finite).")
    if number < 0 or (number == 0 and not allow_zero):
        qualifier = "tidak boleh negatif" if allow_zero else "harus lebih besar dari nol"
        raise ValueError(f"{name} {qualifier}.")
    return number


def calculate_performance_ratio(
    energy_grid_kwh: float,
    glob_inc_kwh_m2: float,
    installed_power_kwp: float,
) -> dict[str, float | str]:
    """Hitung PR untuk grid-connected standar tanpa koreksi self-consumption/storage.

    Periode E_Grid dan GlobInc harus sama. Formula: E_Grid / (GlobInc * PnomPV).
    """
    energy = _positive_finite("Energi grid (kWh)", energy_grid_kwh, allow_zero=True)
    irradiation = _positive_finite("GlobInc (kWh/m²)", glob_inc_kwh_m2)
    power = _positive_finite("Kapasitas terpasang (kWp)", installed_power_kwp)
    denominator = irradiation * power
    pr = energy / denominator
    return {
        "nama": "Performance Ratio (PR)",
        "nilai": pr,
        "persen": pr * 100.0,
        "formula": "PR = E_Grid / (GlobInc × PnomPV)",
        "catatan": "Periode energi dan iradiasi harus sama; formula ini untuk sistem grid-connected standar.",
    }


def calculate_cuf(
    energy_kwh: float,
    installed_power_kw: float,
    period_hours: float,
) -> dict[str, float | str]:
    """Hitung CUF berdasarkan energi aktual, kapasitas, dan durasi periode."""
    energy = _positive_finite("Energi aktual (kWh)", energy_kwh, allow_zero=True)
    power = _positive_finite("Kapasitas terpasang (kW)", installed_power_kw)
    hours = _positive_finite("Durasi periode (jam)", period_hours)
    cuf = energy / (power * hours)
    return {
        "nama": "Capacity Utilization Factor (CUF)",
        "nilai": cuf,
        "persen": cuf * 100.0,
        "formula": "CUF = E_actual / (P_installed × jam_periode)",
        "catatan": "Gunakan energi, kapasitas, dan durasi dari periode yang sama.",
    }


def calculate_energy_difference(
    actual_energy_kwh: float,
    reference_energy_kwh: float,
) -> dict[str, float | str | None]:
    """Hitung selisih energi aktual terhadap energi referensi."""
    actual = _positive_finite("Energi aktual (kWh)", actual_energy_kwh, allow_zero=True)
    reference = _positive_finite("Energi referensi (kWh)", reference_energy_kwh, allow_zero=True)
    difference = actual - reference
    percentage = (difference / reference * 100.0) if reference > 0 else None
    return {
        "nama": "Selisih Energi",
        "selisih_kwh": difference,
        "persentase_terhadap_referensi": percentage,
        "formula": "ΔE = E_actual − E_reference",
        "catatan": "Nilai positif menunjukkan energi aktual lebih besar daripada referensi.",
    }
