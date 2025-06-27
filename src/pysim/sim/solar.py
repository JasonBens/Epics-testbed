import time
import random
import channel_access as ca
from states import States, State
from setpoints import Setpoints, Setpoint


class Simulator:
    # Baseline total power for the solar simulation
    _TOTAL_POWER_BASELINE: float = 100.0
    # Maximum deviation from the baseline power
    _TOTAL_POWER_MAX_DEVIATION: float = 25.0
    # Weight for the previous total power in the weighted average
    _TOTAL_POWER_WEIGHTING: float = 0.9
    # Maximum slew rate for power allocation
    _POWER_ALLOC_MAX_SLEW_RATE: float = 10.0

    # Initial values
    _TOTAL_POWER_INIT: float = _TOTAL_POWER_BASELINE
    _MAX_POWER_ALLOC_INIT: float = 0.0

    def states_factory(self, total_power: float, max_power_alloc: float) -> States:
        return States(
            {
                "total_power": State("SIM:SOLAR:TOTAL_POWER", total_power),
                "max_power_alloc": State("SIM:SOLAR:MAX_POWER_ALLOC", max_power_alloc),
            }
        )

    def __init__(self):
        self._current_states = self.states_factory(
            self._TOTAL_POWER_INIT, self._MAX_POWER_ALLOC_INIT
        )
        self._previous_states = self._current_states
        self._setpoints = Setpoints(
            {"power_alloc": Setpoint("SIM:SOLAR:POWER_ALLOC_SETPOINT")}
        )

    def calculate_total_power(self) -> float:
        """
        Calculates the total power available to the solar powerplant.
        The total power is the weighted average between the previous total
        power with a random deviation added, and the baseline power
        This is then clamped to keep things realistic.
        """
        # Convenience definitions
        baseline = self._TOTAL_POWER_BASELINE
        weight = self._TOTAL_POWER_WEIGHTING
        max_deviation = self._TOTAL_POWER_MAX_DEVIATION

        prev_power = self._previous_states["total_power"]
        deviation = random.uniform(-max_deviation, max_deviation)

        total_power = weight * (prev_power + deviation) + (1 - weight) * baseline
        return clamp(0, total_power, baseline * 2)

    def calculate_max_power_allocated(self, setpoint) -> float:
        """
        Calculates the maximum power allocatable, based on the desired setpoint.
        This includes non-idealities such as slew rate.
        """
        prev_alloc = self._previous_states["max_power_alloc"]
        delta = setpoint - prev_alloc
        if delta > 0:
            # Need to increase the power allocation
            new_alloc = prev_alloc + min(delta, self._POWER_ALLOC_MAX_SLEW_RATE)
        else:
            # Need to decrease the power allocation
            new_alloc = prev_alloc - min(-delta, self._POWER_ALLOC_MAX_SLEW_RATE)
        return new_alloc

    def start(self):
        """
        Starts the solar simulator.
        """
        # Wait for the solar IOC to start
        while ca.get("SOLAR:IS_RUNNING") is None:
            print("Waiting for the solar IOC to connect...")
            time.sleep(5)

        self.current_setpoints = self._setpoints.read_setpoints()

        while not ca.put("SOLAR:IS_RUNNING", 1):
            time.sleep(5)
        print("Solar simulator started.")

    def tick(self):
        """
        Performs one tick of the solar simulation.
        """
        self._previous_states = self._current_states
        current_setpoints = self._setpoints.read_setpoints()

        self._current_states = self.states_factory(
            self.calculate_total_power(),
            self.calculate_max_power_allocated(current_setpoints["power_alloc"]),
        )
        self._current_states.write_states()


def clamp(number: float, lower: float, upper: float) -> float:
    return max(lower, min(number, upper))
