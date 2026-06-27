from dataclasses import dataclass


@dataclass
class SimulationConfig:

    days: int = 30
    runs: int = 10

    base_seed: int | None = None

    inventory_capacity: int = 300
    threshold_percentage: float = 0.7
    initial_inventory: int = 100
    arrival_lambda: int = 45
    triage_servers: int = 2
    crt_servers: int = 1
    lcd_servers: int = 3
    workday_minutes: int = 480
    overtime_minutes: int = 120
    employee_daily_cost: float = 400000
    crt_cost: float = 15000
    lcd_cost: float = 8000

    max_blocked_percentage: float = 0.05
    max_overtime_percentage: float = 0.10
    minimum_acceptance_rate: float = 0.95

    def __post_init__(self):

        if self.days <= 0:
            raise ValueError(
                "La cantidad de dias simulados debe ser mayor que cero."
            )

        if self.runs <= 0:
            raise ValueError(
                "La cantidad de corridas debe ser mayor que cero."
            )

        if self.base_seed is not None and self.base_seed < 0:
            raise ValueError(
                "La semilla base no puede ser negativa."
            )

        if self.inventory_capacity <= 0:
            raise ValueError(
                "La capacidad del deposito debe ser mayor que cero."
            )

        if self.initial_inventory < 0:
            raise ValueError(
                "El stock inicial no puede ser negativo."
            )

        if self.initial_inventory > self.inventory_capacity:
            raise ValueError(
                "El stock inicial no puede superar la capacidad del deposito."
            )

        if self.arrival_lambda < 0:
            raise ValueError(
                "Las llegadas promedio no pueden ser negativas."
            )

        if (
            self.triage_servers <= 0
            or self.crt_servers <= 0
            or self.lcd_servers <= 0
        ):
            raise ValueError(
                "La cantidad de servidores debe ser mayor que cero."
            )

        percentage_fields = {
            "threshold_percentage": self.threshold_percentage,
            "max_blocked_percentage": self.max_blocked_percentage,
            "max_overtime_percentage": self.max_overtime_percentage,
            "minimum_acceptance_rate": self.minimum_acceptance_rate,
        }

        for field_name, value in percentage_fields.items():
            if value < 0 or value > 1:
                raise ValueError(
                    f"{field_name} debe estar entre 0 y 1."
                )
