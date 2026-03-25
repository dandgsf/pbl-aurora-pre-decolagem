from src.ai_analysis import generate_assisted_analysis
from src.checks import evaluate_telemetry
from src.energy import calculate_energy_analysis

from .conftest import make_record


def test_generate_assisted_analysis_marks_critical_risk():
    record = make_record(
        scenario_id="TEST-CRITICAL",
        structural_integrity=0,
        tank_pressure_bar=44.0,
        communication_status="FAIL",
    )
    readiness_result = evaluate_telemetry(record)
    energy_analysis = calculate_energy_analysis(
        total_capacity_kwh=record["total_capacity_kwh"],
        current_charge_pct=record["current_charge_pct"],
        estimated_launch_consumption_kwh=record["estimated_launch_consumption_kwh"],
        loss_pct=record["energy_loss_pct"],
    )

    analysis = generate_assisted_analysis(record, readiness_result, energy_analysis)

    assert analysis["classification"] == "Crítico"
    assert any("Abortar a decolagem" in item for item in analysis["risk_suggestions"])
    assert "TEST-CRITICAL" in analysis["prompt"]
