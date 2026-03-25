"""Visualizações em pandas para a telemetria da missão Aurora."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "telemetry_samples.csv"


def format_scenario_labels(scenarios):
    """Quebra o identificador do cenário em duas linhas para melhorar a leitura."""

    labels = []
    for scenario in scenarios:
        prefix, _, suffix = str(scenario).partition("-")
        labels.append(f"{prefix}\n{suffix}" if suffix else str(scenario))
    return labels


def load_telemetry_dataframe(file_path):
    """Carrega a telemetria em um DataFrame do pandas com tipos consistentes."""

    dataframe = pd.read_csv(file_path)
    numeric_columns = [
        "internal_temp_c",
        "external_temp_c",
        "structural_integrity",
        "energy_level_pct",
        "tank_pressure_bar",
        "total_capacity_kwh",
        "current_charge_pct",
        "estimated_launch_consumption_kwh",
        "energy_loss_pct",
    ]
    dataframe[numeric_columns] = dataframe[numeric_columns].apply(pd.to_numeric)
    return dataframe


def build_dashboard_dataframe(dataframe):
    """Monta um recorte amigável para inspeção e visualização."""

    dashboard = dataframe[
        [
            "scenario_id",
            "internal_temp_c",
            "external_temp_c",
            "energy_level_pct",
            "tank_pressure_bar",
            "communication_status",
        ]
    ].copy()
    dashboard["communication_ok"] = dashboard["communication_status"].eq("OK")
    return dashboard


def generate_telemetry_chart(output_file, file_path=DATA_FILE):
    """Gera um gráfico-resumo dos principais indicadores da telemetria."""

    dataframe = load_telemetry_dataframe(file_path)
    scenarios = dataframe["scenario_id"]
    scenario_labels = format_scenario_labels(scenarios)
    positions = list(range(len(scenarios)))

    figure, axes = plt.subplots(3, 1, figsize=(18, 15), constrained_layout=True)

    axes[0].bar(positions, dataframe["internal_temp_c"], color="#1f77b4")
    axes[0].axhline(18, color="#2ca02c", linestyle="--", linewidth=1)
    axes[0].axhline(35, color="#d62728", linestyle="--", linewidth=1)
    axes[0].set_title("Temperatura interna por cenário")
    axes[0].set_ylabel("°C")
    axes[0].set_xlabel("Cenário")

    axes[1].bar(positions, dataframe["energy_level_pct"], color="#ff7f0e")
    axes[1].axhline(70, color="#d62728", linestyle="--", linewidth=1)
    axes[1].set_title("Nível de energia por cenário")
    axes[1].set_ylabel("%")
    axes[1].set_xlabel("Cenário")

    axes[2].bar(positions, dataframe["tank_pressure_bar"], color="#17becf")
    axes[2].axhline(30, color="#2ca02c", linestyle="--", linewidth=1)
    axes[2].axhline(40, color="#d62728", linestyle="--", linewidth=1)
    axes[2].set_title("Pressão dos tanques por cenário")
    axes[2].set_ylabel("bar")
    axes[2].set_xlabel("Cenário")
    for axis in axes:
        axis.set_xlim(-0.6, len(positions) - 0.4)
        axis.set_xticks(positions)
        axis.set_xticklabels(scenario_labels, fontsize=8)
        axis.tick_params(axis="x", labelbottom=True, pad=6)
        axis.margins(x=0.01)
        axis.grid(axis="y", alpha=0.15, linestyle=":")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_file, dpi=160, bbox_inches="tight")
    plt.close(figure)


def main():
    chart_file = PROJECT_ROOT / "assets" / "prints" / "telemetry_dashboard.png"
    generate_telemetry_chart(chart_file)
    print(f"Gráfico gerado em: {chart_file}")


if __name__ == "__main__":
    main()
