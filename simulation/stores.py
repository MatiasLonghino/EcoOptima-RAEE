import simpy


class PlantStores:

    def __init__(self, env):

        self.inventory = simpy.Store(env)

        self.crt_queue = simpy.Store(env)

        self.lcd_queue = simpy.Store(env)