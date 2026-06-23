from dataclasses import dataclass


@dataclass
class SimulationConfig:

    days: int = 30

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
    
    def __post_init__(self):

        if self.inventory_capacity <= 0:
            raise ValueError(
                "La capacidad del depósito debe ser mayor que cero."
            )

        if self.initial_inventory < 0:
            raise ValueError(
                "El stock inicial no puede ser negativo."
            )

        if self.initial_inventory > self.inventory_capacity:
            raise ValueError(
                "El stock inicial no puede superar la capacidad del depósito."
            )
