from src.checks import evaluate_telemetry

from .conftest import make_record


def test_evaluate_telemetry_accepts_nominal_scenario():
    result = evaluate_telemetry(make_record())

    assert result["ready"] is True
    assert result["decision"] == "PRONTO PARA DECOLAR"
    assert result["anomalies"] == []


def test_evaluate_telemetry_flags_multiple_anomalies():
    result = evaluate_telemetry(
        make_record(
            internal_temp_c=41.0,
            structural_integrity=0,
            tank_pressure_bar=44.0,
            communication_status="FAIL",
        )
    )

    assert result["ready"] is False
    assert result["decision"] == "DECOLAGEM ABORTADA"
    assert "Temperatura interna fora da faixa segura." in result["anomalies"]
    assert "Integridade estrutural comprometida." in result["anomalies"]
    assert "Pressão dos tanques fora da faixa segura." in result["anomalies"]
    assert "Falha em módulo crítico: Comunicação." in result["anomalies"]
