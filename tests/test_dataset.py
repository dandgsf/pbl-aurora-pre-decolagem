from src.checks import evaluate_telemetry
from src.main import DATA_FILE, load_telemetry


def test_telemetry_csv_has_at_least_25_rows():
    records = load_telemetry(DATA_FILE)
    assert len(records) >= 25


def test_scenario_ids_are_unique():
    scenario_ids = [record["scenario_id"] for record in load_telemetry(DATA_FILE)]
    assert len(scenario_ids) == len(set(scenario_ids))


def test_reference_scenarios_keep_expected_decisions():
    records = {record["scenario_id"]: record for record in load_telemetry(DATA_FILE)}

    assert evaluate_telemetry(records["AURORA-01"])["decision"] == "PRONTO PARA DECOLAR"
    assert evaluate_telemetry(records["AURORA-02"])["decision"] == "DECOLAGEM ABORTADA"
    assert evaluate_telemetry(records["AURORA-03"])["decision"] == "DECOLAGEM ABORTADA"
