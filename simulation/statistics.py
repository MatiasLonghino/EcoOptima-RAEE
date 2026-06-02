from dataclasses import dataclass, field


@dataclass
class Statistics:

    # Acumuladores finales

    processed_crt: int = 0

    processed_lcd: int = 0

    processed_irrecoverable: int = 0

    total_cost: float = 0

    overtime_days: int = 0

    # Series temporales
    time_history: list = field(default_factory=list)

    inventory_history: list = field(default_factory=list)

    crt_history: list = field(default_factory=list)

    lcd_history: list = field(default_factory=list)

    irrecoverable_history: list = field(default_factory=list)

    cost_history: list = field(default_factory=list)

    def average_inventory(self):

        if not self.inventory_history:
            return 0

        return (
            sum(self.inventory_history)
            / len(self.inventory_history)
        )