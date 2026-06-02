import simpy

from simulation.entities import Monitor
from simulation.stores import PlantStores
from simulation.statistics import Statistics
from simulation.model import PlantModel
from simulation.random_manager import RandomManager
from simulation.statistical_tests import run_mean_test


class Simulator:

    def __init__(self, config):

        # Guarda la configuración general de la simulación
        self.config = config

    def run(self):

        # Inicializa el objeto donde se guardarán las estadísticas
        stats = Statistics()

        random_manager = RandomManager.from_config(self.config)
        mean_test_manager = RandomManager.from_config(self.config)

        mean_test = run_mean_test(
            mean_test_manager.uniform_generator.generate_many(
                self.config.mean_test_sample_size
            ),
            self.config.mean_test_alpha
        )

        # Crea el entorno de simulación de SimPy
        env = simpy.Environment()

        # Crea los depósitos y colas internas de la planta
        stores = PlantStores(env)

        # Crea el modelo de procesamiento.
        # Importante:
        # Se asume que PlantModel inicia internamente los procesos
        # de triage, CRT y LCD.
        PlantModel(
            env,
            stores,
            self.config,
            stats,
            random_manager,
        )

        # Identificador único para cada monitor
        monitor_id = 0

        # Variable que indica si el día siguiente tendrá horas extra
        overtime_next_day = False

        # ---------------------------------------------------------
        # CARGA DEL INVENTARIO INICIAL
        # ---------------------------------------------------------
        # No usamos stores.inventory.items.append(...)
        # porque eso modifica directamente la lista interna del Store.
        #
        # En SimPy se debe usar put(), ya que put() dispara los eventos
        # necesarios para que los procesos que están esperando con get()
        # puedan continuar.
        # ---------------------------------------------------------

        for _ in range(self.config.initial_inventory):

            monitor_id += 1

            stores.inventory.put(
                Monitor(monitor_id)
            )

        # ---------------------------------------------------------
        # SIMULACIÓN DÍA POR DÍA
        # ---------------------------------------------------------

        for _ in range(self.config.days):

            # -----------------------------------------------------
            # 1. GENERACIÓN DE LLEGADAS DIARIAS
            # -----------------------------------------------------

            arrivals = random_manager.arrival_distribution.sample()

            # Agrega los monitores nuevos al inventario.
            # Nuevamente usamos put(), no append().
            for _ in range(arrivals):

                monitor_id += 1

                stores.inventory.put(
                    Monitor(monitor_id)
                )

            # -----------------------------------------------------
            # 2. DEFINICIÓN DE LA JORNADA LABORAL
            # -----------------------------------------------------

            # Minutos normales de trabajo del día
            daily_minutes = self.config.workday_minutes

            # Cantidad total de empleados activos
            employees = (
                self.config.triage_servers
                + self.config.crt_servers
                + self.config.lcd_servers
            )

            # Costo laboral diario base
            labor_cost = (
                employees
                * self.config.employee_daily_cost
            )

            # Si el día anterior se superó el umbral crítico,
            # entonces este día se trabaja con horas extra.
            if overtime_next_day:

                # Las horas extra aumentan el tiempo disponible
                # de procesamiento durante este día.
                daily_minutes += self.config.overtime_minutes

                # Se incrementa el costo laboral por horas extra.
                # Ojo: esto multiplica todo el costo diario por 1.5.
                # Si más adelante querés más precisión, convendría separar
                # costo normal y costo extra.
                labor_cost *= 1.5

                # Se registra un día con horas extra
                stats.overtime_days += 1

            # Acumula el costo total
            stats.total_cost += labor_cost

            # -----------------------------------------------------
            # 3. EJECUCIÓN DE LA JORNADA
            # -----------------------------------------------------
            # Se corre el entorno durante la cantidad de minutos
            # disponibles para este día.
            # -----------------------------------------------------

            env.run(
                until=env.now + daily_minutes
            )

            # -----------------------------------------------------
            # 4. CÁLCULO DEL INVENTARIO FINAL DEL DÍA
            # -----------------------------------------------------
            # Este inventario representa todas las unidades que siguen
            # dentro del sistema:
            #
            # - unidades todavía sin clasificar en inventory
            # - unidades esperando procesamiento CRT
            # - unidades esperando procesamiento LCD
            #
            # No incluye las unidades ya procesadas ni las irrecuperables
            # ya descartadas.
            # -----------------------------------------------------

            inventory_level = (
                len(stores.inventory.items)
                + len(stores.crt_queue.items)
                + len(stores.lcd_queue.items)
            )

            # Guarda el inventario diario
            stats.inventory_history.append(
                inventory_level
            )

            # Guarda producción acumulada de CRT
            stats.crt_history.append(
                stats.processed_crt
            )

            # Guarda producción acumulada de LCD
            stats.lcd_history.append(
                stats.processed_lcd
            )

            # Guarda producción acumulada de irrecuperables
            stats.irrecoverable_history.append(
                stats.processed_irrecoverable
            )

            # Guarda costo acumulado
            stats.cost_history.append(
                stats.total_cost
            )

            # -----------------------------------------------------
            # 5. ACTIVACIÓN DE HORAS EXTRA PARA EL DÍA SIGUIENTE
            # -----------------------------------------------------

            threshold = (
                self.config.inventory_capacity
                * self.config.threshold_percentage
            )

            # Si el inventario supera el umbral crítico,
            # el día siguiente tendrá horas extra.
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

            # Resultado de la prueba de los promedios
            "MEAN_TEST": {
                "SAMPLE_SIZE": mean_test.sample_size,
                "SAMPLE_MEAN": round(
                    mean_test.sample_mean,
                    4
                ),
                "Z_STATISTIC": round(
                    mean_test.z_statistic,
                    4
                ),
                "CRITICAL_VALUE": round(
                    mean_test.critical_value,
                    4
                ),
                "ALPHA": mean_test.alpha,
                "REJECT_NULL": mean_test.reject_null,
                "DECISION": mean_test.decision,
            },

            # Total de CRT procesados
            "CRT":
                stats.processed_crt,

            # Total de LCD procesados
            "LCD":
                stats.processed_lcd,

            # Total de irrecuperables procesados
            "IRRECOVERABLE":
                stats.processed_irrecoverable,

            # Inventario final en planta
            "FINAL_INVENTORY":
                final_inventory,

            # Inventario promedio
            "AVG_INVENTORY":
                round(
                    stats.average_inventory(),
                    2
                ),

            # Costo total acumulado
            "TOTAL_COST":
                round(
                    stats.total_cost,
                    2
                ),

            # Porcentaje de días con horas extra
            "OVERTIME_PERCENT":
                round(
                    (
                        stats.overtime_days
                        / self.config.days
                    ) * 100,
                    2
                ),

            # Días simulados para eje X
            "DAYS":
                list(
                    range(
                        1,
                        self.config.days + 1
                    )
                ),

            # Historial diario del inventario
            "INVENTORY_HISTORY":
                stats.inventory_history,

            # Historial acumulado de CRT procesados
            "CRT_HISTORY":
                stats.crt_history,

            # Historial acumulado de LCD procesados
            "LCD_HISTORY":
                stats.lcd_history,

            # Historial acumulado de irrecuperables
            "IRRECOVERABLE_HISTORY":
                stats.irrecoverable_history,

            # Historial del costo acumulado
            "COST_HISTORY":
                stats.cost_history,
        }