import time
import solar
import channel_access as ca


def init_simulation():
    """
    Sets the initial state of the simulation and pushes it to the PVs.
    """
    solar.set_solar_states({"SIM:SOLAR:TOTAL_POWER": 100.0})
    ca.put("SIM:IS_RUNNING", 0)
    print("Simulation initialized")


def run_simulation():
    ca.put("SIM:IS_RUNNING", 1)
    print("Simulation started.")
    while True:
        solar_setpoints: dict = solar.get_solar_setpoints()
        solar_states = solar.run_solar_simulation(solar_setpoints)
        solar.set_solar_states(solar_states)
        time.sleep(0.5)


def main():
    init_simulation()
    run_simulation()


if __name__ == "__main__":
    main()
