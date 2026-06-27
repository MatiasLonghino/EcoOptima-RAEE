class PlantModel:

    def __init__(
        self,
        env,
        stores,
        config,
        stats,
        rng
    ):

        self.env = env
        self.stores = stores
        self.config = config
        self.stats = stats
        self.rng = rng

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

        return self.rng.choice(categorias, p=probabilidades)

    def triage_worker(self):

        while True:

            monitor = yield (
                self.stores.inventory.get()
            )

            self.stats.in_triage += 1

            triage_time = self.rng.uniform(
                10,
                15
            )

            yield self.env.timeout(
                triage_time
            )

            category = self.classify()

            monitor.category = category

            self.stats.in_triage -= 1

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

            self.stats.in_crt_processing += 1

            process_time = max(
                0,
                self.rng.normal(
                    20,
                    3
                )
            )

            yield self.env.timeout(
                process_time
            )

            monitor.processed = True

            self.stats.in_crt_processing -= 1

            self.stats.processed_crt += 1

            self.stats.total_processing_cost += (
                self.config.crt_cost
            )

            self.stats.total_cost += (
                self.config.crt_cost
            )

    def lcd_worker(self):

        while True:

            monitor = yield (
                self.stores.lcd_queue.get()
            )

            self.stats.in_lcd_processing += 1

            process_time = max(
                0,
                self.rng.normal(
                    37,
                    4
                )
            )

            yield self.env.timeout(
                process_time
            )

            monitor.processed = True

            self.stats.in_lcd_processing -= 1

            self.stats.processed_lcd += 1

            self.stats.total_processing_cost += (
                self.config.lcd_cost
            )

            self.stats.total_cost += (
                self.config.lcd_cost
            )
