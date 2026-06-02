from dataclasses import dataclass, field


@dataclass
class Statistics:

    processed_crt: int = 0

    processed_lcd: int = 0

    processed_irrecoverable: int = 0

    total_cost: float = 0

    overtime_days: int = 0

    inventory_history: list = field(default_factory=list)

    def average_inventory(self):

        if not self.inventory_history:
            return 0

        return (
            sum(self.inventory_history)
            / len(self.inventory_history)
        )