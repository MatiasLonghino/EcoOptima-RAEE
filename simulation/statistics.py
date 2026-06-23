from dataclasses import dataclass, field


@dataclass
class Statistics:

    # Acumuladores finales de procesamiento
    processed_crt: int = 0
    processed_lcd: int = 0
    processed_irrecoverable: int = 0
    total_cost: float = 0
    overtime_days: int = 0

    # Acumuladores de capacidad del depósito
    total_admitted: int = 0
    total_rejected: int = 0
    max_storage_inventory: int = 0
    capacity_violations: int = 0

    # Series temporales generales
    time_history: list = field(default_factory=list)
    inventory_history: list = field(default_factory=list)
    crt_history: list = field(default_factory=list)
    lcd_history: list = field(default_factory=list)
    irrecoverable_history: list = field(default_factory=list)
    cost_history: list = field(default_factory=list)

    # Series temporales de admisión al depósito
    admitted_history: list = field(default_factory=list)
    rejected_history: list = field(default_factory=list)
    storage_inventory_history: list = field(default_factory=list)

    def average_inventory(self):
        """
        Calcula el inventario promedio registrado
        durante la simulación.
        """

        if not self.inventory_history:
            return 0

        return (
            sum(self.inventory_history)
            / len(self.inventory_history)
        )