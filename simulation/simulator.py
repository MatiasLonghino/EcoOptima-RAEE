import simpy
import numpy as np

from simulation.entities import Monitor
from simulation.stores import PlantStores
from simulation.statistics import Statistics
from simulation.model import PlantModel


class Simulator:

    def __init__(self, config):

        self.config = config

    def run(self):

        stats = Statistics()

        env = simpy.Environment()

        stores = PlantStores(env)

        model = PlantModel(
            env,
            stores,
            self.config,
            stats
        )

        monitor_id = 0

        overtime_next_day = False

        for _ in range(
            self.config.initial_inventory
        ):

            monitor_id += 1

            stores.inventory.items.append(
                Monitor(monitor_id)
            )

        for day in range(
            self.config.days
        ):

            arrivals = np.random.poisson(
                self.config.arrival_lambda
            )

            for _ in range(arrivals):

                monitor_id += 1

                stores.inventory.items.append(
                    Monitor(monitor_id)
                )

            daily_minutes = (
                self.config.workday_minutes
            )

            employees = (
                self.config.triage_servers
                + self.config.crt_servers
                + self.config.lcd_servers
            )

            labor_cost = (
                employees
                * self.config.employee_daily_cost
            )

            if overtime_next_day:

                daily_minutes += (
                    self.config.overtime_minutes
                )

                labor_cost *= 1.5

                stats.overtime_days += 1

            stats.total_cost += labor_cost

            env.run(
                until=env.now
                + daily_minutes
            )

            inventory_level = (
                len(stores.inventory.items)
                + len(stores.crt_queue.items)
                + len(stores.lcd_queue.items)
)
            # Guardar ocupación del día
            stats.inventory_history.append(
                inventory_level
            )
            # Calcular umbral crítico
            threshold = (
                self.config.inventory_capacity
                * self.config.threshold_percentage
            )
            # Definir si mañana habrá horas extras
            overtime_next_day = (
                inventory_level
                >= threshold
            )

        return {

            "CRT":
                stats.processed_crt,

            "LCD":
                stats.processed_lcd,

            "IRRECOVERABLE":
                stats.processed_irrecoverable,

            "FINAL_INVENTORY":
            (
                len(stores.inventory.items)
                + len(stores.crt_queue.items)
                + len(stores.lcd_queue.items)
            ),  

            "AVG_INVENTORY":
                round(
                    stats.average_inventory(),
                    2
                ),

            "TOTAL_COST":
                round(
                    stats.total_cost,
                    2
                ),

            "OVERTIME_PERCENT":
                round(
                    (
                        stats.overtime_days
                        / self.config.days
                    ) * 100,
                    2
                )
        }