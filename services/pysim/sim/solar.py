import math
import time
import random
from enum import Enum, auto
import channel_access as ca
from states import States, State
from setpoints import Setpoints, Setpoint


class Simulator:
    class PowerConsts:
        INIT_VAL = 100  # Initial value
        BASELINE_VAL = 100  # Baseline power level for the wind simulation
        MIN_VAL = 0  # Minimum power level available
        MAX_VAL = 200  # Maximum power level available
        MAX_DEVIATION = 5.0  # Maximum deviation from the baseline power level

    class AllocConsts:
        INIT_VAL = 0.0  # Initial value
        MAX_SLEW_RATE = 10.0  # Maximum slew rate for power allocation

    class SolarStateMachine:
        MIN_CLOUD_COVER = 0.1  # Minimum cloud cover percentage when cloudy
        MAX_CLOUD_COVER = 0.5  # Maximum cloud cover percentage when cloudy

        class SolarState(Enum):
            NORMAL = auto()
            CLOUDY = auto()

        class TransitionProbability:
            def __init__(
                self,
                population: list["Simulator.SolarStateMachine.SolarState"],
                weights: list[int],
            ):
                self.population = population
                self.weights = weights

        _TRANSITION_PROBABILITY = {
            SolarState.NORMAL: TransitionProbability(list(SolarState), [99, 1]),
            SolarState.CLOUDY: TransitionProbability(list(SolarState), [5, 95]),
        }

        def __init__(self):
            self._state = self.SolarState.NORMAL
            self.cloud_cover = 0

        def tick(self):
            prev_state = self._state

            choices = self._TRANSITION_PROBABILITY[self._state]
            self._state = random.choices(choices.population, choices.weights, k=1)[0]

            if prev_state != self._state:
                # Transition occured.
                match self._state:
                    case self.SolarState.NORMAL:
                        print("Solar state machine transitioned to NORMAL.")
                        self.cloud_cover = 0
                    case self.SolarState.CLOUDY:
                        print("Solar state machine transitioned to CLOUDY.")
                        self.cloud_cover = random.uniform(
                            self.MIN_CLOUD_COVER, self.MAX_CLOUD_COVER
                        )
                print(f"Current cloud cover: {self.cloud_cover:.0%}")

    def states_factory(self, total_power: float, max_power_alloc: float) -> States:
        return States(
            {
                "total_power": State("SIM:SOLAR:TOTAL_POWER", total_power),
                "max_power_alloc": State("SIM:SOLAR:MAX_POWER_ALLOC", max_power_alloc),
            }
        )

    def __init__(self):
        self._current_states = self.states_factory(
            self.PowerConsts.INIT_VAL, self.AllocConsts.INIT_VAL
        )
        self._previous_states = self._current_states
        self._setpoints = Setpoints(
            {"power_alloc": Setpoint("SIM:SOLAR:POWER_ALLOC_SETPOINT")}
        )

        self._solar_state_machine = self.SolarStateMachine()

        self._current_timestep = 0

    def calculate_total_power(self) -> float:
        """
        Calculates the total power available to the solar powerplant.
        The total power is the weighted average between the previous total
        power with a random deviation added, and the baseline power
        This is then clamped to keep things realistic.
        """
        raw_power = self._calculate_total_power(
            current_timestep=self._current_timestep,
            baseline=self.PowerConsts.BASELINE_VAL,
            min_val=self.PowerConsts.MIN_VAL,
            max_val=self.PowerConsts.MAX_VAL,
            max_deviation=self.PowerConsts.MAX_DEVIATION,
        )
        return raw_power * (1.0 - self._solar_state_machine.cloud_cover)

    def calculate_max_power_allocation(self, setpoint) -> float:
        """
        Calculates the maximum power allocatable, based on the desired setpoint.
        This includes non-idealities such as slew rate.
        """
        prev_alloc = self._previous_states["max_power_alloc"]
        delta = setpoint - prev_alloc
        if delta > 0:
            # Need to increase the power allocation
            new_alloc = prev_alloc + min(delta, self.AllocConsts.MAX_SLEW_RATE)
        else:
            # Need to decrease the power allocation
            new_alloc = prev_alloc - min(-delta, self.AllocConsts.MAX_SLEW_RATE)
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

        self._solar_state_machine.tick()
        self._current_timestep += 1

        self._current_states = self.states_factory(
            self.calculate_total_power(),
            self.calculate_max_power_allocation(current_setpoints["power_alloc"]),
        )
        self._current_states.write_states()

    @staticmethod
    def clamp(number: float, lower: float, upper: float) -> float:
        return max(lower, min(number, upper))

    @staticmethod
    def _calculate_total_power(
        current_timestep: int,
        baseline: float,
        min_val: float,
        max_val: float,
        max_deviation: float,
    ) -> float:
        deviation = random.uniform(-max_deviation, max_deviation)
        total_power = (
            math.sin(current_timestep / 500.0 * 2 * math.pi) * (baseline / 2)
            + baseline
            + deviation
        )
        return Simulator.clamp(total_power, min_val, max_val)
