import random
import time
import epics

# Remember that this is the simulation, not the control system.  We read the setpoints and update the state accordingly.
solar_setpoint_keys = {"SIM:SOLAR:ALLOCATED_POWER", "SIM:SOLAR:UNALLOCATED_POWER"}
solar_state_keys = {"SIM:SOLAR:TOTAL_POWER"}


def get_setpoints_from_keys(keys: set) -> dict:
    """
    Returns a dictionary with the current setpoints of the control system.
    """
    setpoints = {key: epics.caget(key) for key in keys}
    missing_keys = [key for key, value in setpoints.items() if value is None]
    if missing_keys:
        print(f"Error: Unable to read the following keys: {', '.join(missing_keys)}.")
    return setpoints


def set_state_from_dict(state: dict):
    """
    Sets the state of control system based on the passed dictionary.
    """
    result = {key: epics.caput(key, value) for key, value in state.items()}
    failed_puts = [key for key, success in result.items() if success != 1]
    if failed_puts:
        print(f"Failed to set the following keys: {', '.join(failed_puts)}.")


def get_solar_setpoints() -> dict:
    """
    Returns a dictionary with the current setpoints of the solar records.
    """
    return get_setpoints_from_keys(solar_setpoint_keys)


def run_solar_simulation(solar_setpoints: dict) -> dict:
    """
    Runs the solar simulation based on the provided dictionary of setpoints.
    """
    state = {}
    state["SIM:SOLAR:TOTAL_POWER"] = random.randint(0, 100)
    return state


def set_solar_states(states: dict):
    """
    Sets the state of the solar records based on the passed dictionary.
    """
    set_state_from_dict(states)


def init_simulation():
    """
    Sets the initial state of the simulation and pushes it to the PVs.
    """
    set_solar_states({"SIM:SOLAR:TOTAL_POWER": 100.0})
    epics.caput("SIM:IS_RUNNING", 0)
    print("Simulation initialized")


def run_simulation():
    epics.caput("SIM:IS_RUNNING", 1)
    print("Simulation started.")
    while True:
        solar_setpoints: dict = get_solar_setpoints()
        solar_states = run_solar_simulation(solar_setpoints)
        set_solar_states(solar_states)
        time.sleep(0.5)


def main():
    init_simulation()
    run_simulation()


if __name__ == "__main__":
    main()
