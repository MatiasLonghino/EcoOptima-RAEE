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

    employee_daily_cost: float = 30

    crt_cost: float = 1500

    lcd_cost: float = 800

    mean_test_sample_size: int = 30

    mean_test_alpha: float = 0.05

    generator_method: str = "lehmer"

    random_seed: int = 12345

    generator_multiplier: int = 48271

    generator_increment: int = 0

    generator_modulus: int = 2147483647

    middle_square_seed: int = 1234

    middle_square_digits: int = 4

    additive_seed_1: int = 1942

    additive_seed_2: int = 2372

    additive_seed_3: int = 5131

    additive_seed_4: int = 3317

    additive_lag_a: int = 1

    additive_lag_b: int = 4