"""Executa o projeto e cria artefatos de saída para o relatório."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.visualization import generate_telemetry_chart

OUTPUT_TXT = PROJECT_ROOT / "assets" / "prints" / "execution_output.txt"
OUTPUT_PNG = PROJECT_ROOT / "assets" / "prints" / "execution_output.png"
TEST_OUTPUT_TXT = PROJECT_ROOT / "assets" / "prints" / "test_output.txt"
TEST_OUTPUT_PNG = PROJECT_ROOT / "assets" / "prints" / "test_output.png"
OUTPUT_DASHBOARD = PROJECT_ROOT / "assets" / "prints" / "telemetry_dashboard.png"
ABSOLUTE_PATH_PATTERN = re.compile(r"[A-Za-z]:\\\\[^\s:]+")


def render_text_to_image(text, output_file):
    lines = text.splitlines() or [""]
    font = ImageFont.load_default()
    max_width = max(font.getbbox(line)[2] for line in lines) + 40
    line_height = font.getbbox("Ag")[3] + 6
    image_height = max(200, line_height * len(lines) + 40)

    image = Image.new("RGB", (max_width, image_height), color=(18, 18, 18))
    draw = ImageDraw.Draw(image)

    y = 20
    for line in lines:
        draw.text((20, y), line, fill=(200, 240, 200), font=font)
        y += line_height

    image.save(output_file)


def build_child_env():
    child_env = os.environ.copy()
    child_env["PYTHONIOENCODING"] = "utf-8"
    child_env["MPLBACKEND"] = "Agg"
    return child_env


def run_command(command):
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=build_child_env(),
    )
    output = result.stdout
    if result.stderr:
        output = f"{output}\n{result.stderr}".strip()
    if result.returncode != 0:
        raise RuntimeError(
            f"Falha ao executar {' '.join(command)}.\n\nSaída capturada:\n{output}"
        )
    return output


def sanitize_output(text):
    sanitized = text.replace(str(PROJECT_ROOT), ".")
    sanitized = sanitized.replace(str(Path.home()), "~")
    sanitized = ABSOLUTE_PATH_PATTERN.sub("[local-path]", sanitized)
    sanitized_lines = [
        line
        for line in sanitized.splitlines()
        if not line.strip().startswith("rootdir:")
    ]
    return "\n".join(sanitized_lines).strip()


def build_execution_preview(text):
    decisions = Counter()
    sample_lines = []
    current_scenario = None

    for raw_line in text.splitlines():
        if raw_line.startswith("CENÁRIO: "):
            current_scenario = raw_line.split(": ", 1)[1].strip()
        elif raw_line.startswith("Decisão final: "):
            decision = raw_line.split(": ", 1)[1].strip()
            decisions[decision] += 1
            if current_scenario:
                sample_lines.append(f"- {current_scenario}: {decision}")

    preview_lines = [
        "EXECUCAO DO PROJETO AURORA",
        "",
        f"Cenarios processados: {sum(decisions.values())}",
        f"Prontos para decolar: {decisions['PRONTO PARA DECOLAR']}",
        f"Decolagens abortadas: {decisions['DECOLAGEM ABORTADA']}",
        "",
        "Amostra da saida real:",
        *sample_lines[:10],
        "",
        "Log completo salvo em assets/prints/execution_output.txt",
    ]
    return "\n".join(preview_lines)


def build_test_preview(text):
    summary_line = next(
        (
            line.strip()
            for line in reversed(text.splitlines())
            if "passed" in line and "in" in line
        ),
        "Resultado final indisponivel.",
    )
    collected_line = next(
        (
            line.strip()
            for line in text.splitlines()
            if line.strip().startswith("collected ")
        ),
        "collected 0 items",
    )
    preview_lines = [
        "RESULTADO DOS TESTES",
        "",
        "Ferramenta: pytest",
        collected_line,
        summary_line,
        "",
        "Arquivos validados:",
        "- tests/test_ai_analysis.py",
        "- tests/test_checks.py",
        "- tests/test_dataset.py",
        "- tests/test_energy.py",
        "",
        "Log completo salvo em assets/prints/test_output.txt",
    ]
    return "\n".join(preview_lines)


def main():
    OUTPUT_TXT.parent.mkdir(parents=True, exist_ok=True)

    execution_output = run_command([sys.executable, "-m", "src.main"])
    test_output = run_command(
        [sys.executable, "-m", "pytest", "-q", "--disable-warnings"]
    )
    execution_output = sanitize_output(execution_output)
    test_output = sanitize_output(test_output)

    OUTPUT_TXT.write_text(execution_output, encoding="utf-8")
    TEST_OUTPUT_TXT.write_text(test_output, encoding="utf-8")

    render_text_to_image(build_execution_preview(execution_output), OUTPUT_PNG)
    render_text_to_image(build_test_preview(test_output), TEST_OUTPUT_PNG)
    generate_telemetry_chart(OUTPUT_DASHBOARD)

    print(
        "Saídas geradas em: "
        f"{OUTPUT_TXT}, {OUTPUT_PNG}, {TEST_OUTPUT_TXT}, {TEST_OUTPUT_PNG} "
        f"e {OUTPUT_DASHBOARD}"
    )


if __name__ == "__main__":
    main()
