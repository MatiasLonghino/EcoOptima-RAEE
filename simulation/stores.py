import simpy


class PlantStores:

    def __init__(self, env, inventory_capacity):

        self.inventory = simpy.Store(
            env, 
            capacity=inventory_capacity)

        self.crt_queue = simpy.Store(env)

        self.lcd_queue = simpy.Store(env)