import random
from typing import NamedTuple
import channel_access as ca

# Remember that this is the simulation, not the control system.  We read the setpoints and update the state accordingly.
SETPOINT_KEYS = {"SIM:SOLAR:ALLOCATED_POWER", "SIM:SOLAR:UNALLOCATED_POWER"}
STATE_KEYS = {"SIM:SOLAR:TOTAL_POWER"}


class Constants:
    """
    Constants for the solar simulation total power calculations.
    """

    TOTAL_POWER_BASELINE: float = 100.0  # Baseline total power for the solar simulation
    TOTAL_POWER_MAX_DEVIATION: float = 25.0  # Maximum deviation from the baseline power
    TOTAL_POWER_WEIGHTING: float = (
        0.9  # Weight for the previous total power in the weighted average
    )


# TODO: Pass SolarState as a parameter to solar.py functions instead of using globals
# # class SolarState:
#     """
#     Represents the state and setpoints of the solar simulation.  Remember that this is the simulation, not the control system.
#     We read the setpoints and update the state accordingly.
#     """

#     def _init__(self):
#         self.setpoints = {
#             "allocated_power": {"name": "SIM:SOLAR:ALLOCATED_POWER"},
#             "unallocated_power": {"name": "SIM:SOLAR:UNALLOCATED_POWER"},
#         }
#         self.states = {"total_power": {"name": "SIM:SOLAR:TOTAL_POWER"}}


def clamp(number, lower, upper):
    return max(lower, min(number, upper))


def get_solar_setpoints() -> dict:
    """
    Returns a dictionary with the current setpoints of the solar records.
    """
    return ca.get_setpoints_from_keys(SETPOINT_KEYS)


def calculate_total_power() -> float:
    """
    Calculates the total power available to the solar powerplant.
    The total power is the weighted average between the previous total
    power with a random deviation added, and the baseline power
    This is then clamped to keep things realistic.
    """
    prev_total_power = ca.get("SIM:SOLAR:TOTAL_POWER", 100)
    deviation: float = random.uniform(
        -Constants.TOTAL_POWER_MAX_DEVIATION, Constants.TOTAL_POWER_MAX_DEVIATION
    )
    total_power = (
        Constants.TOTAL_POWER_WEIGHTING * (prev_total_power + deviation)
        + (1 - Constants.TOTAL_POWER_WEIGHTING) * Constants.TOTAL_POWER_BASELINE
    )
    return clamp(0, total_power, Constants.TOTAL_POWER_BASELINE * 2)


def run_solar_simulation(solar_setpoints: dict) -> dict:
    """
    Runs the solar simulation based on the provided dictionary of setpoints.
    """
    state = {}
    state["SIM:SOLAR:TOTAL_POWER"] = calculate_total_power()

    return state


def set_solar_states(states: dict):
    """
    Sets the state of the solar records based on the passed dictionary.
    """
    ca.set_state_from_dict(states)
