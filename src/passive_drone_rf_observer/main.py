import time
from .config import load_config
from .simulation import SimulationManager


def main() -> None:
    cfg = load_config()
    print(f"Starting passive-drone-rf-observer simulation for {cfg.simulation_duration_s}s")

    manager = SimulationManager(cfg)
    manager.start()
    time.sleep(cfg.simulation_duration_s)
    manager.stop()

    print("Simulation finished")
