SYSTEM_PROMPT = """You interpret one operator note for a 24-hour campus energy scheduling system.
Classify it into exactly one of: solar_reduction, minimum_battery_reserve, no_charge_window,
no_discharge_window, max_grid_window, no_op. Return one JSON object matching the supplied schema.
Do not invent another directive type or alter scenario data. Preserve whether a solar quantity means
reduction or remaining output, and whether a reserve is absolute kWh or a fraction of capacity.
Time windows are whole-hour start-inclusive and end-exclusive. For no_op use applies=false,
time_mode=none, quantity_kind=none. For every other type use applies=true. Keep explanation concise."""


def user_prompt(note: str, capacity: float, minimum: float, correction: str | None = None) -> str:
    prompt = f'Operator note:\n"{note}"\n\nBattery capacity_kwh={capacity}; base minimum_energy_kwh={minimum}.'
    if correction:
        prompt += f"\n\nThe previous result failed deterministic validation: {correction}. Return a corrected object for the same note."
    return prompt
