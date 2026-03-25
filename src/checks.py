"""Regras de verificação da telemetria para a missão Aurora."""

SAFE_LIMITS = {
    "internal_temp_c": {"min": 18.0, "max": 35.0, "unit": "C"},
    "external_temp_c": {"min": -120.0, "max": 50.0, "unit": "C"},
    "energy_level_pct": {"min": 70.0, "max": 100.0, "unit": "%"},
    "tank_pressure_bar": {"min": 30.0, "max": 40.0, "unit": "bar"},
}

CRITICAL_MODULE_FIELDS = {
    "navigation_status": "Navegação",
    "communication_status": "Comunicação",
    "propulsion_status": "Propulsão",
    "life_support_status": "Suporte de vida",
}


def _between(value, minimum, maximum):
    return minimum <= value <= maximum


def _normalize_status(value):
    return str(value).strip().upper()


def _make_check(name, passed, detail):
    return {
        "name": name,
        "passed": passed,
        "status": "OK" if passed else "ALERTA",
        "detail": detail,
    }


def evaluate_telemetry(record):
    """Avalia um cenário de telemetria e decide se a nave pode decolar."""

    checks = []
    anomalies = []

    internal_ok = _between(
        record["internal_temp_c"],
        SAFE_LIMITS["internal_temp_c"]["min"],
        SAFE_LIMITS["internal_temp_c"]["max"],
    )
    detail = (
        f'{record["internal_temp_c"]:.1f} C dentro da faixa '
        f'{SAFE_LIMITS["internal_temp_c"]["min"]:.0f} a '
        f'{SAFE_LIMITS["internal_temp_c"]["max"]:.0f} C'
    )
    if not internal_ok:
        detail = (
            f'{record["internal_temp_c"]:.1f} C fora da faixa '
            f'{SAFE_LIMITS["internal_temp_c"]["min"]:.0f} a '
            f'{SAFE_LIMITS["internal_temp_c"]["max"]:.0f} C'
        )
        anomalies.append("Temperatura interna fora da faixa segura.")
    checks.append(_make_check("Temperatura interna", internal_ok, detail))

    external_ok = _between(
        record["external_temp_c"],
        SAFE_LIMITS["external_temp_c"]["min"],
        SAFE_LIMITS["external_temp_c"]["max"],
    )
    detail = (
        f'{record["external_temp_c"]:.1f} C dentro da faixa '
        f'{SAFE_LIMITS["external_temp_c"]["min"]:.0f} a '
        f'{SAFE_LIMITS["external_temp_c"]["max"]:.0f} C'
    )
    if not external_ok:
        detail = (
            f'{record["external_temp_c"]:.1f} C fora da faixa '
            f'{SAFE_LIMITS["external_temp_c"]["min"]:.0f} a '
            f'{SAFE_LIMITS["external_temp_c"]["max"]:.0f} C'
        )
        anomalies.append("Temperatura externa fora da faixa segura.")
    checks.append(_make_check("Temperatura externa", external_ok, detail))

    structure_ok = int(record["structural_integrity"]) == 1
    detail = "Integridade estrutural confirmada." if structure_ok else "Falha de integridade estrutural."
    if not structure_ok:
        anomalies.append("Integridade estrutural comprometida.")
    checks.append(_make_check("Integridade estrutural", structure_ok, detail))

    energy_ok = _between(
        record["energy_level_pct"],
        SAFE_LIMITS["energy_level_pct"]["min"],
        SAFE_LIMITS["energy_level_pct"]["max"],
    )
    detail = (
        f'{record["energy_level_pct"]:.1f}% dentro da faixa '
        f'{SAFE_LIMITS["energy_level_pct"]["min"]:.0f}% a '
        f'{SAFE_LIMITS["energy_level_pct"]["max"]:.0f}%'
    )
    if not energy_ok:
        detail = (
            f'{record["energy_level_pct"]:.1f}% abaixo do mínimo '
            f'de {SAFE_LIMITS["energy_level_pct"]["min"]:.0f}%'
        )
        anomalies.append("Nível de energia abaixo do mínimo operacional.")
    checks.append(_make_check("Nível de energia", energy_ok, detail))

    pressure_ok = _between(
        record["tank_pressure_bar"],
        SAFE_LIMITS["tank_pressure_bar"]["min"],
        SAFE_LIMITS["tank_pressure_bar"]["max"],
    )
    detail = (
        f'{record["tank_pressure_bar"]:.1f} bar dentro da faixa '
        f'{SAFE_LIMITS["tank_pressure_bar"]["min"]:.0f} a '
        f'{SAFE_LIMITS["tank_pressure_bar"]["max"]:.0f} bar'
    )
    if not pressure_ok:
        detail = (
            f'{record["tank_pressure_bar"]:.1f} bar fora da faixa '
            f'{SAFE_LIMITS["tank_pressure_bar"]["min"]:.0f} a '
            f'{SAFE_LIMITS["tank_pressure_bar"]["max"]:.0f} bar'
        )
        anomalies.append("Pressão dos tanques fora da faixa segura.")
    checks.append(_make_check("Pressão dos tanques", pressure_ok, detail))

    module_failures = []
    for field, label in CRITICAL_MODULE_FIELDS.items():
        module_ok = _normalize_status(record[field]) == "OK"
        detail = f"{label}: {_normalize_status(record[field])}"
        if not module_ok:
            module_failures.append(label)
        checks.append(_make_check(f"Módulo crítico - {label}", module_ok, detail))

    if module_failures:
        anomalies.append("Falha em módulo crítico: " + ", ".join(module_failures) + ".")

    ready = all(item["passed"] for item in checks)
    decision = "PRONTO PARA DECOLAR" if ready else "DECOLAGEM ABORTADA"

    return {
        "ready": ready,
        "decision": decision,
        "checks": checks,
        "anomalies": anomalies,
    }
