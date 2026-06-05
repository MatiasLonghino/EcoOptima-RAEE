import simpy
import numpy as np

from simulation.entities import Monitor
from simulation.stores import PlantStores
from simulation.statistics import Statistics
from simulation.model import PlantModel


class Simulator:

    def __init__(self, config):

        # Guarda la configuración general de la simulación
        self.config = config

    def run(self):

        # Inicializa el objeto donde se guardarán las estadísticas
        stats = Statistics()

        # Crea el entorno de simulación de SimPy
        env = simpy.Environment()

        # Crea los depósitos y colas internas de la planta
        stores = PlantStores(env)

        # Crea el modelo de procesamiento.
        # Se asume que PlantModel inicia internamente los procesos
        # de triage, CRT y LCD.
        model = PlantModel(
            env,
            stores,
            self.config,
            stats
        )

        # Identificador único para cada monitor
        monitor_id = 0

        # Variable que indica si el día siguiente tendrá horas extra
        overtime_next_day = False

        # ---------------------------------------------------------
        # CARGA DEL INVENTARIO INICIAL
        # ---------------------------------------------------------

        for _ in range(self.config.initial_inventory):

            monitor_id += 1

            stores.inventory.put(
                Monitor(monitor_id)
            )

        # ---------------------------------------------------------
        # SIMULACIÓN DÍA POR DÍA
        # ---------------------------------------------------------

        for day in range(self.config.days):

            # -----------------------------------------------------
            # 1. GENERACIÓN DE LLEGADAS DIARIAS
            # -----------------------------------------------------

            arrivals = np.random.poisson(
                self.config.arrival_lambda
            )

            for _ in range(arrivals):

                monitor_id += 1

                stores.inventory.put(
                    Monitor(monitor_id)
                )

            # -----------------------------------------------------
            # 2. DEFINICIÓN DE LA JORNADA LABORAL
            # -----------------------------------------------------

            daily_minutes = self.config.workday_minutes

            employees = (
                self.config.triage_servers
                + self.config.crt_servers
                + self.config.lcd_servers
            )

            # Costo laboral diario base.
            # Este costo depende de la cantidad de servidores activos.
            labor_cost = (
                employees
                * self.config.employee_daily_cost
            )

            # Si el día anterior se superó el umbral crítico,
            # este día se trabaja con horas extra.
            if overtime_next_day:

                daily_minutes += self.config.overtime_minutes

                # Mantengo tu criterio original:
                # si hay horas extra, se multiplica el costo laboral diario.
                labor_cost *= 1.5

                stats.overtime_days += 1

            # -----------------------------------------------------
            # 3. REGISTRO DEL ESTADO ANTES DE PROCESAR EL DÍA
            # -----------------------------------------------------
            # Estos valores son necesarios porque processed_crt y
            # processed_lcd son acumulados.
            #
            # Para calcular el costo diario de procesamiento, necesitamos
            # saber cuántas unidades se procesaron solamente durante
            # este día.
            # -----------------------------------------------------

            previous_crt = stats.processed_crt
            previous_lcd = stats.processed_lcd

            # -----------------------------------------------------
            # 4. EJECUCIÓN DE LA JORNADA
            # -----------------------------------------------------

            env.run(
                until=env.now + daily_minutes
            )

            # -----------------------------------------------------
            # 5. CÁLCULO DE UNIDADES PROCESADAS EN EL DÍA
            # -----------------------------------------------------

            daily_crt = (
                stats.processed_crt
                - previous_crt
            )

            daily_lcd = (
                stats.processed_lcd
                - previous_lcd
            )

            # -----------------------------------------------------
            # 6. CÁLCULO DEL COSTO DE PROCESAMIENTO
            # -----------------------------------------------------
            # Se agregan al costo total los costos variables por
            # procesar unidades CRT y LCD.
            #
            # No se consideran costos por capacidad ociosa,
            # acumulación completa de capacidad ni penalizaciones,
            # porque actualmente no forman parte del modelo.
            # -----------------------------------------------------

            processing_cost = (
                daily_crt * self.config.crt_cost
                + daily_lcd * self.config.lcd_cost
            )

            # -----------------------------------------------------
            # 7. CÁLCULO DEL COSTO TOTAL DIARIO
            # -----------------------------------------------------
            # El costo total diario ahora está compuesto por:
            #
            # - costo laboral
            # - costo de procesamiento de CRT
            # - costo de procesamiento de LCD
            # -----------------------------------------------------

            daily_total_cost = (
                labor_cost
                + processing_cost
            )

            # Acumula el costo total del sistema
            stats.total_cost += daily_total_cost

            # -----------------------------------------------------
            # 8. CÁLCULO DEL INVENTARIO FINAL DEL DÍA
            # -----------------------------------------------------

            inventory_level = (
                len(stores.inventory.items)
                + len(stores.crt_queue.items)
                + len(stores.lcd_queue.items)
            )

            stats.inventory_history.append(
                inventory_level
            )

            stats.crt_history.append(
                stats.processed_crt
            )

            stats.lcd_history.append(
                stats.processed_lcd
            )

            stats.irrecoverable_history.append(
                stats.processed_irrecoverable
            )

            stats.cost_history.append(
                stats.total_cost
            )

            # -----------------------------------------------------
            # 9. ACTIVACIÓN DE HORAS EXTRA PARA EL DÍA SIGUIENTE
            # -----------------------------------------------------

            threshold = (
                self.config.inventory_capacity
                * self.config.threshold_percentage
            )

            overtime_next_day = (
                inventory_level >= threshold
            )

        # ---------------------------------------------------------
        # RESULTADOS FINALES
        # ---------------------------------------------------------

        final_inventory = (
            len(stores.inventory.items)
            + len(stores.crt_queue.items)
            + len(stores.lcd_queue.items)
        )

        return {

            "CRT":
                stats.processed_crt,

            "LCD":
                stats.processed_lcd,

            "IRRECOVERABLE":
                stats.processed_irrecoverable,

            "FINAL_INVENTORY":
                final_inventory,

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
                ),

            "DAYS":
                list(
                    range(
                        1,
                        self.config.days + 1
                    )
                ),

            "INVENTORY_HISTORY":
                stats.inventory_history,

            "CRT_HISTORY":
                stats.crt_history,

            "LCD_HISTORY":
                stats.lcd_history,

            "IRRECOVERABLE_HISTORY":
                stats.irrecoverable_history,

            "COST_HISTORY":
                stats.cost_history,
        }