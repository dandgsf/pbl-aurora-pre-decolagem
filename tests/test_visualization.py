from pathlib import Path

from src.visualization import generate_telemetry_chart


def test_generate_telemetry_chart_creates_image(tmp_path):
    output_file = tmp_path / "telemetry_dashboard.png"

    generate_telemetry_chart(output_file)

    assert output_file.exists()
    assert output_file.stat().st_size > 0
