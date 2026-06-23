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

        # ---------------------------------------------------------
        # VALIDACIÓN DEL STOCK INICIAL
        # ---------------------------------------------------------
        # Evita iniciar una simulación con más equipos que la
        # capacidad física del depósito.
        # ---------------------------------------------------------

        if (
            self.config.initial_inventory
            > self.config.inventory_capacity
        ):
            raise ValueError(
                "El stock inicial no puede superar la capacidad "
                "máxima del depósito."
            )

        # Inicializa el objeto donde se guardarán las estadísticas
        stats = Statistics()

        # Crea el entorno de simulación de SimPy
        env = simpy.Environment()

        # Crea el depósito y las colas internas.
        # El Store inventory debe tener como capacidad máxima
        # self.config.inventory_capacity.
        stores = PlantStores(
            env,
            self.config.inventory_capacity
        )

        # Crea el modelo de procesamiento
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

        # Registra el inventario físico inicial del depósito.
        initial_storage_inventory = len(
            stores.inventory.items
        )

        stats.max_storage_inventory = (
            initial_storage_inventory
        )

        # ---------------------------------------------------------
        # SIMULACIÓN DÍA POR DÍA
        # ---------------------------------------------------------

        for day in range(self.config.days):

            # -----------------------------------------------------
            # 1. GENERACIÓN Y ADMISIÓN DE LLEGADAS DIARIAS
            # -----------------------------------------------------

            arrivals = np.random.poisson(
                self.config.arrival_lambda
            )

            # Inventario físico actualmente dentro del depósito.
            current_storage_inventory = len(
                stores.inventory.items
            )

            # Espacio disponible en el depósito.
            available_space = (
                self.config.inventory_capacity
                - current_storage_inventory
            )

            # Protección adicional ante valores inesperados.
            available_space = max(
                0,
                available_space
            )

            # Solo ingresan los equipos que entran físicamente.
            admitted = min(
                arrivals,
                available_space
            )

            # Los restantes no ingresan ni quedan esperando
            # espacio dentro de SimPy.
            rejected = arrivals - admitted

            # Se crean únicamente los equipos admitidos.
            for _ in range(admitted):

                monitor_id += 1

                stores.inventory.put(
                    Monitor(monitor_id)
                )

            # Inventario físico luego de la llegada.
            storage_inventory_after_arrivals = len(
                stores.inventory.items
            )

            # Registro de admisiones y rechazos del día.
            stats.total_admitted += admitted
            stats.total_rejected += rejected

            stats.admitted_history.append(
                admitted
            )

            stats.rejected_history.append(
                rejected
            )

            # Registra el máximo inventario físico observado.
            stats.max_storage_inventory = max(
                stats.max_storage_inventory,
                storage_inventory_after_arrivals
            )

            # Verificación explícita de la restricción física.
            if (
                storage_inventory_after_arrivals
                > self.config.inventory_capacity
            ):
                stats.capacity_violations += 1

                raise RuntimeError(
                    "El inventario físico del depósito superó "
                    "la capacidad máxima permitida."
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

            base_labor_cost = (
                employees
                * self.config.employee_daily_cost
            )

            overtime_extra_cost = 0

            if overtime_next_day:

                daily_minutes += self.config.overtime_minutes

                overtime_extra_cost = (
                    base_labor_cost
                    * 0.5
                )

                stats.overtime_days += 1

            daily_labor_cost = (
                base_labor_cost
                + overtime_extra_cost
            )

            stats.total_base_labor_cost += base_labor_cost
            stats.total_labor_cost += daily_labor_cost
            stats.total_overtime_extra_cost += overtime_extra_cost
            stats.total_cost += daily_labor_cost

            processing_cost_before_day = (
                stats.total_processing_cost
            )
            total_cost_before_day = (
                stats.total_cost
                - daily_labor_cost
            )

            # -----------------------------------------------------
            # 3. EJECUCIÓN DE LA JORNADA
            # -----------------------------------------------------

            env.run(
                until=env.now + daily_minutes
            )

            daily_processing_cost = (
                stats.total_processing_cost
                - processing_cost_before_day
            )

            daily_total_cost = (
                stats.total_cost
                - total_cost_before_day
            )

            # -----------------------------------------------------
            # 4. INVENTARIO FINAL DEL DÍA
            # -----------------------------------------------------
            # inventory_level representa el total de equipos
            # pendientes dentro de todo el sistema:
            # depósito + cola CRT + cola LCD.
            # -----------------------------------------------------

            inventory_level = (
                len(stores.inventory.items)
                + len(stores.crt_queue.items)
                + len(stores.lcd_queue.items)
            )

            # Inventario físico dentro del depósito únicamente.
            storage_inventory = len(
                stores.inventory.items
            )

            # Historial del inventario total del sistema.
            stats.inventory_history.append(
                inventory_level
            )

            # Historial del inventario físico del depósito.
            stats.storage_inventory_history.append(
                storage_inventory
            )

            # Actualiza y verifica el máximo físico diario.
            stats.max_storage_inventory = max(
                stats.max_storage_inventory,
                storage_inventory
            )

            if (
                storage_inventory
                > self.config.inventory_capacity
            ):
                stats.capacity_violations += 1

                raise RuntimeError(
                    "El inventario físico del depósito superó "
                    "la capacidad máxima permitida."
                )

            # Historiales acumulados de procesamiento.
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

            stats.processing_cost_history.append(
                stats.total_processing_cost
            )

            stats.base_labor_cost_history.append(
                stats.total_base_labor_cost
            )

            stats.labor_cost_history.append(
                stats.total_labor_cost
            )

            stats.overtime_extra_cost_history.append(
                stats.total_overtime_extra_cost
            )

            stats.daily_cost_history.append(
                daily_total_cost
            )

            stats.daily_processing_cost_history.append(
                daily_processing_cost
            )

            stats.daily_base_labor_cost_history.append(
                base_labor_cost
            )

            stats.daily_labor_cost_history.append(
                daily_labor_cost
            )

            stats.daily_overtime_extra_cost_history.append(
                overtime_extra_cost
            )

            # -----------------------------------------------------
            # 5. ACTIVACIÓN DE HORAS EXTRA PARA EL DÍA SIGUIENTE
            # -----------------------------------------------------
            # Se conserva la regla actual: usa el inventario total
            # del sistema, incluyendo las colas internas.
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

        final_storage_inventory = len(
            stores.inventory.items
        )

        return {

            "CRT": stats.processed_crt,
            "LCD": stats.processed_lcd,
            "IRRECOVERABLE": stats.processed_irrecoverable,

            # Inventario total pendiente en la planta.
            "FINAL_INVENTORY": final_inventory,

            # Inventario físico dentro del depósito.
            "FINAL_STORAGE_INVENTORY":
                final_storage_inventory,

            "AVG_INVENTORY": round(
                stats.average_inventory(),
                2
            ),

            "TOTAL_COST": round(
                stats.total_cost,
                2
            ),

            "TOTAL_PROCESSING_COST": round(
                stats.total_processing_cost,
                2
            ),

            "TOTAL_BASE_LABOR_COST": round(
                stats.total_base_labor_cost,
                2
            ),

            "TOTAL_LABOR_COST": round(
                stats.total_labor_cost,
                2
            ),

            "TOTAL_OVERTIME_EXTRA_COST": round(
                stats.total_overtime_extra_cost,
                2
            ),

            "OVERTIME_PERCENT": round(
                (
                    stats.overtime_days
                    / self.config.days
                ) * 100,
                2
            ),

            # Nuevas métricas de capacidad.
            "TOTAL_ADMITTED": stats.total_admitted,
            "TOTAL_REJECTED": stats.total_rejected,

            "MAX_STORAGE_INVENTORY":
                stats.max_storage_inventory,

            "CAPACITY_VIOLATIONS":
                stats.capacity_violations,

            "CAPACITY_OK": (
                stats.max_storage_inventory
                <= self.config.inventory_capacity
                and stats.capacity_violations == 0
            ),

            "DAYS": list(
                range(
                    1,
                    self.config.days + 1
                )
            ),

            # Inventario total dentro del sistema.
            "INVENTORY_HISTORY":
                stats.inventory_history,

            # Inventario físico del depósito.
            "STORAGE_INVENTORY_HISTORY":
                stats.storage_inventory_history,

            "ADMITTED_HISTORY":
                stats.admitted_history,

            "REJECTED_HISTORY":
                stats.rejected_history,

            "CRT_HISTORY":
                stats.crt_history,

            "LCD_HISTORY":
                stats.lcd_history,

            "IRRECOVERABLE_HISTORY":
                stats.irrecoverable_history,

            "COST_HISTORY":
                stats.cost_history,

            "PROCESSING_COST_HISTORY":
                stats.processing_cost_history,

            "BASE_LABOR_COST_HISTORY":
                stats.base_labor_cost_history,

            "LABOR_COST_HISTORY":
                stats.labor_cost_history,

            "OVERTIME_EXTRA_COST_HISTORY":
                stats.overtime_extra_cost_history,

            "DAILY_COST_HISTORY":
                stats.daily_cost_history,

            "DAILY_PROCESSING_COST_HISTORY":
                stats.daily_processing_cost_history,

            "DAILY_BASE_LABOR_COST_HISTORY":
                stats.daily_base_labor_cost_history,

            "DAILY_LABOR_COST_HISTORY":
                stats.daily_labor_cost_history,

            "DAILY_OVERTIME_EXTRA_COST_HISTORY":
                stats.daily_overtime_extra_cost_history,
        }
