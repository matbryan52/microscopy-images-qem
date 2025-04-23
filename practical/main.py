import pathlib
import numpy as np
from qem_practical.simulator import STEMImageSimulator
from qem_practical.simulator_ui import simulator_ui
rootdir = pathlib.Path(__file__).parent

sim_data = np.load(rootdir / "data" / "particles.npz")
image = sim_data["data"]
extent = sim_data["extent"]
simulator = STEMImageSimulator(image, extent, current=1., drift_speed=0.1)
simulator_ui(simulator).servable("stem-simulator")
