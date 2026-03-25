import pytest

from src.energy import calculate_energy_analysis


def test_calculate_energy_analysis_matches_reference_values():
    result = calculate_energy_analysis(
        total_capacity_kwh=1200,
        current_charge_pct=92,
        estimated_launch_consumption_kwh=260,
        loss_pct=8,
    )

    assert result["stored_energy_kwh"] == pytest.approx(1104.0)
    assert result["usable_energy_kwh"] == pytest.approx(1015.68)
    assert result["remaining_after_launch_kwh"] == pytest.approx(755.68)
    assert result["launch_cycles_supported"] == pytest.approx(3.9064615384)
    assert result["launch_supported"] is True
