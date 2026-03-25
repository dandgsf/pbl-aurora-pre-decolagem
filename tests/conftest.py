"""Utilitarios compartilhados para os testes do projeto Aurora."""

BASE_RECORD = {
    "scenario_id": "TEST-BASE",
    "internal_temp_c": 24.0,
    "external_temp_c": -45.0,
    "structural_integrity": 1,
    "energy_level_pct": 92.0,
    "tank_pressure_bar": 38.0,
    "navigation_status": "OK",
    "communication_status": "OK",
    "propulsion_status": "OK",
    "life_support_status": "OK",
    "total_capacity_kwh": 1200.0,
    "current_charge_pct": 92.0,
    "estimated_launch_consumption_kwh": 260.0,
    "energy_loss_pct": 8.0,
}


def make_record(**overrides):
    record = BASE_RECORD.copy()
    record.update(overrides)
    return record
