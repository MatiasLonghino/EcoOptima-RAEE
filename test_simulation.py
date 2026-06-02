# test_simulation.py

from simulation.config import SimulationConfig
from simulation.simulator import Simulator

config = SimulationConfig()

sim = Simulator(config)

results = sim.run()

print(results)