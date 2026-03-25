"""Gera evidencias reais de analise assistida por IA para o relatorio."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.ai_analysis import build_ai_prompt
from src.energy import calculate_energy_analysis
from src.main import DATA_FILE, load_telemetry
from src.checks import evaluate_telemetry

OUTPUT_JSON = PROJECT_ROOT / "report" / "ai_assisted_analysis.json"
OUTPUT_MARKDOWN = PROJECT_ROOT / "report" / "ai_assisted_analysis.md"
REFERENCE_SCENARIOS = ("AURORA-01", "AURORA-02", "AURORA-03")
MODEL_CANDIDATES = ("gpt-4.1-mini", "gpt-4o-mini", "gpt-4.1-nano")


def load_reference_records():
    records = {item["scenario_id"]: item for item in load_telemetry(DATA_FILE)}
    return [records[scenario_id] for scenario_id in REFERENCE_SCENARIOS]


def build_request_prompt(record):
    readiness_result = evaluate_telemetry(record)
    energy_analysis = calculate_energy_analysis(
        total_capacity_kwh=record["total_capacity_kwh"],
        current_charge_pct=record["current_charge_pct"],
        estimated_launch_consumption_kwh=record["estimated_launch_consumption_kwh"],
        loss_pct=record["energy_loss_pct"],
    )
    base_prompt = build_ai_prompt(record, readiness_result, energy_analysis)
    request_prompt = (
        f"{base_prompt}\n\n"
        "Responda estritamente em JSON com estas chaves:\n"
        "- scenario_id: string\n"
        "- classification: string\n"
        "- anomalies: array de strings\n"
        "- risk_suggestions: array de strings\n"
        "- summary: string curta em portugues\n"
    )
    return request_prompt, readiness_result, energy_analysis


def request_chat_completion(prompt, model):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY nao encontrado no ambiente.")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Voce e um analista tecnico de missoes espaciais. "
                    "Siga o formato JSON solicitado pelo usuario sem texto adicional."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    data = json.dumps(payload).encode("utf-8")
    request = Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urlopen(request, timeout=60) as response:
        body = json.loads(response.read().decode("utf-8"))
    return json.loads(body["choices"][0]["message"]["content"])


def request_with_fallback(prompt):
    last_error = None
    for model in MODEL_CANDIDATES:
        try:
            return model, request_chat_completion(prompt, model)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            last_error = exc
    raise RuntimeError(f"Falha ao consultar os modelos configurados: {last_error}") from last_error


def build_markdown(document):
    lines = [
        "# Evidencia de Analise Assistida por IA",
        "",
        f"- Gerado em: {document['generated_at']}",
        f"- Modelo utilizado: {document['model']}",
        "",
    ]
    for item in document["analyses"]:
        anomalies = item["anomalies"] or ["Nenhuma anomalia reportada pelo LLM."]
        suggestions = item["risk_suggestions"] or ["Nenhuma sugestao adicional reportada pelo LLM."]
        lines.extend(
            [
                f"## {item['scenario_id']}",
                "",
                f"**Classificacao:** {item['classification']}",
                "",
                "**Anomalias identificadas pela IA**",
                "",
                *[f"- {entry}" for entry in anomalies],
                "",
                "**Sugestoes objetivas de risco**",
                "",
                *[f"- {entry}" for entry in suggestions],
                "",
                f"**Resumo:** {item['summary']}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def main():
    analyses = []
    model_used = None

    for record in load_reference_records():
        prompt, readiness_result, energy_analysis = build_request_prompt(record)
        model_used, ai_output = request_with_fallback(prompt)
        analyses.append(
            {
                "scenario_id": record["scenario_id"],
                "prompt": prompt,
                "local_decision": readiness_result["decision"],
                "remaining_after_launch_kwh": round(
                    energy_analysis["remaining_after_launch_kwh"], 2
                ),
                "classification": ai_output["classification"],
                "anomalies": ai_output["anomalies"],
                "risk_suggestions": ai_output["risk_suggestions"],
                "summary": ai_output["summary"],
            }
        )

    document = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": model_used,
        "analyses": analyses,
    }

    OUTPUT_JSON.write_text(
        json.dumps(document, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    OUTPUT_MARKDOWN.write_text(build_markdown(document), encoding="utf-8")
    print(f"Evidencias geradas em: {OUTPUT_JSON} e {OUTPUT_MARKDOWN}")


if __name__ == "__main__":
    main()
