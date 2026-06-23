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

            self.stats.total_processing_cost += (
                self.config.lcd_cost
            )

            self.stats.total_cost += (
                self.config.lcd_cost
            )
