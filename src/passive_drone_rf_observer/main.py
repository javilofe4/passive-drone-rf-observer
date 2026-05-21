import time
from .config import load_config
from .runtime import AppRuntime


def main() -> None:
    cfg = load_config()
    print(f"Starting passive-drone-rf-observer simulation for {cfg.simulation_duration_s}s")

    runtime = AppRuntime(cfg)
    runtime.start()
    time.sleep(cfg.simulation_duration_s)
    runtime.stop()

    print("Simulation finished")
