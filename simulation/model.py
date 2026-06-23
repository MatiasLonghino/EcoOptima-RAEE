import numpy as np

class PlantModel:

    def __init__(
        self,
        env,
        stores,
        config,
        stats
    ):

        self.env = env
        self.stores = stores
        self.config = config
        self.stats = stats

        for _ in range(
            config.triage_servers
        ):
            env.process(
                self.triage_worker()
            )

        for _ in range(
            config.crt_servers
        ):
            env.process(
                self.crt_worker()
            )

        for _ in range(
            config.lcd_servers
        ):
            env.process(
                self.lcd_worker()
            )

    def classify(self):

        categorias = ["IRRECOVERABLE", "LCD", "CRT"]
        probabilidades = [0.10, 0.30, 0.60]
        
        return np.random.choice(categorias, p=probabilidades)

    def triage_worker(self):

        while True:

            monitor = yield (
                self.stores.inventory.get()
            )

            triage_time = np.random.uniform(
                10,
                15
            )

            yield self.env.timeout(
                triage_time
            )

            category = self.classify()

            monitor.category = category

            if category == "IRRECOVERABLE":

                self.stats.processed_irrecoverable += 1

            elif category == "CRT":

                yield (
                    self.stores.crt_queue.put(
                        monitor
                    )
                )

            else:

                yield (
                    self.stores.lcd_queue.put(
                        monitor
                    )
                )

    def crt_worker(self):

        while True:

            monitor = yield (
                self.stores.crt_queue.get()
            )

            process_time = max(
                0,
                np.random.normal(
                    20,
                    3
                )
            )

            yield self.env.timeout(
                process_time
            )

            monitor.processed = True

            self.stats.processed_crt += 1

            self.stats.total_cost += (
                self.config.crt_cost
            )

    def lcd_worker(self):

        while True:

            monitor = yield (
                self.stores.lcd_queue.get()
            )

            process_time = max(
                0,
                np.random.normal(
                    37,
                    4
                )
            )

            yield self.env.timeout(
                process_time
            )

            monitor.processed = True

            self.stats.processed_lcd += 1

            self.stats.total_cost += (
                self.config.lcd_cost
            )
                       
    def admit_daily_arrivals(self, urban_arrivals, agreement_arrivals):
        """
        Calcula cuántos equipos pueden ingresar físicamente
        al depósito y registra los equipos rechazados.
        """

        total_arrivals = urban_arrivals + agreement_arrivals

        current_inventory = len(self.stores.inventory.items)

        available_space = (
            self.config.inventory_capacity
            - current_inventory
        )

        available_space = max(0, available_space)

        admitted = min(
            total_arrivals,
            available_space
        )

        rejected = total_arrivals - admitted

        # Solo se crean e ingresan los equipos admitidos.
        for _ in range(admitted):
            monitor = Monitor()
            yield self.stores.inventory.put(monitor)

        inventory_after_arrivals = len(
            self.stores.inventory.items
        )

        # Registro de llegadas.
        self.stats.urban_arrivals_history.append(
            urban_arrivals
        )

        self.stats.agreement_arrivals_history.append(
            agreement_arrivals
        )

        self.stats.total_arrivals_history.append(
            total_arrivals
        )

        self.stats.admitted_history.append(admitted)
        self.stats.rejected_history.append(rejected)

        self.stats.total_admitted += admitted
        self.stats.total_rejected += rejected

        self.stats.inventory_after_arrivals_history.append(
            inventory_after_arrivals
        )

        # Control de capacidad.
        self.stats.max_inventory_recorded = max(
            self.stats.max_inventory_recorded,
            inventory_after_arrivals
        )

        if inventory_after_arrivals > self.config.inventory_capacity:
            self.stats.capacity_violations += 1

            raise RuntimeError(
                "Se detectó inventario superior a la capacidad "
                "del depósito."
            )

        return {
            "available_space": available_space,
            "admitted": admitted,
            "rejected": rejected,
            "inventory_after_arrivals": inventory_after_arrivals
        }