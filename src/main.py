"""Execução principal do relatório operacional de pré-decolagem."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.ai_analysis import generate_assisted_analysis
from src.checks import evaluate_telemetry
from src.energy import calculate_energy_analysis

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "telemetry_samples.csv"

FLOAT_FIELDS = [
    "internal_temp_c",
    "external_temp_c",
    "energy_level_pct",
    "tank_pressure_bar",
    "total_capacity_kwh",
    "current_charge_pct",
    "estimated_launch_consumption_kwh",
    "energy_loss_pct",
]

INT_FIELDS = ["structural_integrity"]


def load_telemetry(file_path):
    dataframe = pd.read_csv(file_path)
    dataframe[FLOAT_FIELDS] = dataframe[FLOAT_FIELDS].astype(float)
    dataframe[INT_FIELDS] = dataframe[INT_FIELDS].astype(int)
    return dataframe.to_dict(orient="records")


def evaluate_scenario(record):
    readiness_result = evaluate_telemetry(record)
    energy_analysis = calculate_energy_analysis(
        total_capacity_kwh=record["total_capacity_kwh"],
        current_charge_pct=record["current_charge_pct"],
        estimated_launch_consumption_kwh=record["estimated_launch_consumption_kwh"],
        loss_pct=record["energy_loss_pct"],
    )
    ai_analysis = generate_assisted_analysis(record, readiness_result, energy_analysis)
    return {
        "record": record,
        "readiness": readiness_result,
        "energy": energy_analysis,
        "ai": ai_analysis,
    }


def print_scenario(result):
    record = result["record"]
    readiness = result["readiness"]
    energy = result["energy"]
    ai_analysis = result["ai"]

    print("=" * 72)
    print(f'CENÁRIO: {record["scenario_id"]}')
    print("-" * 72)
    print(f'Decisão final: {readiness["decision"]}')
    print("Verificações:")
    for check in readiness["checks"]:
        print(f'  - [{check["status"]}] {check["name"]}: {check["detail"]}')

    print("Análise energética:")
    print(f'  - Energia armazenada: {energy["stored_energy_kwh"]:.2f} kWh')
    print(f'  - Energia utilizável: {energy["usable_energy_kwh"]:.2f} kWh')
    print(f'  - Energia restante após a decolagem: {energy["remaining_after_launch_kwh"]:.2f} kWh')
    print(f'  - Ciclos equivalentes de decolagem suportados: {energy["launch_cycles_supported"]:.2f}')

    print("Análise assistida por IA:")
    print(f'  - Classificação: {ai_analysis["classification"]}')
    print("  - Anomalias:")
    for item in ai_analysis["anomalies"]:
        print(f"    * {item}")
    print("  - Sugestões de risco:")
    for item in ai_analysis["risk_suggestions"]:
        print(f"    * {item}")
    print()


def main():
    print("RELATÓRIO OPERACIONAL DE PRÉ-DECOLAGEM - MISSÃO AURORA")
    print()

    scenarios = load_telemetry(DATA_FILE)
    for scenario in scenarios:
        print_scenario(evaluate_scenario(scenario))


if __name__ == "__main__":
    main()
