"""Apoio à análise assistida por IA para o PBL."""


def classify_risk(readiness_result, energy_analysis):
    """Classifica o risco operacional com base nos achados do cenário."""

    anomalies = readiness_result["anomalies"]
    severe_keywords = ("integridade", "módulo crítico", "pressão", "temperatura interna")

    if any(keyword in " ".join(anomalies).lower() for keyword in severe_keywords):
        return "Crítico"
    if not readiness_result["ready"]:
        return "Alto"
    if not energy_analysis["launch_supported"]:
        return "Alto"
    if energy_analysis["remaining_after_launch_kwh"] < 300:
        return "Moderado"
    return "Baixo"


def build_ai_prompt(record, readiness_result, energy_analysis):
    """Gera um prompt pronto para usar em um LLM."""

    return f"""
Você é um assistente de missão espacial.
Analise os dados de telemetria abaixo e responda em português com:
1. Classificação do cenário.
2. Possíveis anomalias.
3. Sugestões objetivas de risco.

Cenário: {record["scenario_id"]}
Temperatura interna: {record["internal_temp_c"]} C
Temperatura externa: {record["external_temp_c"]} C
Integridade estrutural: {record["structural_integrity"]}
Nível de energia: {record["energy_level_pct"]}%
Pressão dos tanques: {record["tank_pressure_bar"]} bar
Módulo navegação: {record["navigation_status"]}
Módulo comunicação: {record["communication_status"]}
Módulo propulsão: {record["propulsion_status"]}
Módulo suporte de vida: {record["life_support_status"]}
Decisão automática atual: {readiness_result["decision"]}
Energia utilizável: {energy_analysis["usable_energy_kwh"]:.2f} kWh
Energia restante após decolagem: {energy_analysis["remaining_after_launch_kwh"]:.2f} kWh
""".strip()


def generate_assisted_analysis(record, readiness_result, energy_analysis):
    """Gera uma análise inicial para documentar a atividade."""

    anomalies = readiness_result["anomalies"][:]
    if not anomalies:
        anomalies.append("Nenhuma anomalia crítica detectada na telemetria inicial.")

    risk_level = classify_risk(readiness_result, energy_analysis)

    suggestions = []
    if readiness_result["ready"]:
        suggestions.append("Prosseguir com a checagem regressiva e manter monitoramento contínuo.")
    else:
        suggestions.append("Abortar a decolagem até que todas as falhas críticas sejam resolvidas.")

    if record["energy_level_pct"] < 70:
        suggestions.append("Reforçar a carga das baterias antes de uma nova tentativa.")
    if int(record["structural_integrity"]) == 0:
        suggestions.append("Executar inspeção estrutural completa no casco e nos suportes.")
    if str(record["communication_status"]).strip().upper() != "OK":
        suggestions.append("Restabelecer o módulo de comunicação antes da janela de lançamento.")
    if energy_analysis["remaining_after_launch_kwh"] < 250:
        suggestions.append("Reavaliar a margem energética para fases posteriores da missão.")

    if len(suggestions) == 1:
        suggestions.append("Registrar o cenário como referência de operação segura.")

    return {
        "classification": risk_level,
        "anomalies": anomalies,
        "risk_suggestions": suggestions,
        "prompt": build_ai_prompt(record, readiness_result, energy_analysis),
    }
