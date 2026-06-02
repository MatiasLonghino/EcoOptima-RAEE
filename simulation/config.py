from dataclasses import dataclass


@dataclass
class SimulationConfig:

    days: int = 30

    inventory_capacity: int = 300

    threshold_percentage: float = 0.7

    initial_inventory: int = 100

    arrival_lambda: int = 45

    triage_servers: int = 1

    crt_servers: int = 1

    lcd_servers: int = 3

    workday_minutes: int = 480

    overtime_minutes: int = 120

    employee_daily_cost: float = 30

    crt_cost: float = 1500

    lcd_cost: float = 800