from typing import Literal

from pydantic import BaseModel, ConfigDict


DirectiveType = Literal[
    "solar_reduction",
    "minimum_battery_reserve",
    "no_charge_window",
    "no_discharge_window",
    "max_grid_window",
    "no_op",
]


class SemanticDirective(BaseModel):
    model_config = ConfigDict(extra="forbid")

    applies: bool
    directive_type: DirectiveType
    time_mode: Literal["window", "explicit_hours", "none"]
    start_hour: int | None = None
    end_hour: int | None = None
    explicit_hours: list[int] | None = None
    quantity_value: float | None = None
    quantity_kind: Literal[
        "remaining_fraction",
        "remaining_percent",
        "reduction_fraction",
        "reduction_percent",
        "absolute_kwh",
        "battery_capacity_fraction",
        "battery_capacity_percent",
        "none",
    ]
    explanation: str
