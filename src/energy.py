"""Calculos energeticos usados no relatorio operacional."""


def calculate_energy_analysis(
    total_capacity_kwh,
    current_charge_pct,
    estimated_launch_consumption_kwh,
    loss_pct,
):
    """Calcula a energia disponivel antes e depois da decolagem."""

    stored_energy_kwh = total_capacity_kwh * (current_charge_pct / 100)
    usable_energy_kwh = stored_energy_kwh * (1 - (loss_pct / 100))
    remaining_after_launch_kwh = usable_energy_kwh - estimated_launch_consumption_kwh
    launch_cycles_supported = usable_energy_kwh / estimated_launch_consumption_kwh
    launch_supported = remaining_after_launch_kwh >= 0

    return {
        "stored_energy_kwh": stored_energy_kwh,
        "usable_energy_kwh": usable_energy_kwh,
        "remaining_after_launch_kwh": remaining_after_launch_kwh,
        "launch_cycles_supported": launch_cycles_supported,
        "launch_supported": launch_supported,
    }
