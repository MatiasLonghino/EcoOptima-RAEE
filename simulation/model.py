from simulation.random_manager import RandomManager

class PlantModel:

    def __init__(
        self,
        env,
        stores,
        config,
        stats,
        random_manager: RandomManager,
    ):

        self.env = env
        self.stores = stores
        self.config = config
        self.stats = stats
        self.random_manager = random_manager

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

        u = self.random_manager.uniform_generator.next()

        if u <= 0.10:
            return "IRRECOVERABLE"

        elif u <= 0.40:
            return "CRT"

        return "LCD"

    def triage_worker(self):

        while True:

            monitor = yield (
                self.stores.inventory.get()
            )

            triage_time = (
                self.random_manager.triage_time_distribution.sample()
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
                self.random_manager.crt_time_distribution.sample()
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
                self.random_manager.lcd_time_distribution.sample()
            )

            yield self.env.timeout(
                process_time
            )

            monitor.processed = True

            self.stats.processed_lcd += 1

            self.stats.total_cost += (
                self.config.lcd_cost
            )