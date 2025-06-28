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
        MAX_DEVIATION = 25.0  # Maximum deviation from the baseline power level
        FILTER_WEIGHT = 0.9  # Weight for previous value in the running average
        GUST_BASELINE_VAL = (
            BASELINE_VAL  # Baseline power level for the wind simulation when gusting
        )
        GUST_MIN_VAL = 0  # Minimum power level available when gusting
        GUST_MAX_VAL = 300  # Maximum power level available when gusting
        GUST_MAX_DEVIATION = (
            100  # Maximum deviation from the baseline power level when gusting
        )
        GUST_FILTER_WEIGHT = (
            0.9  # Weight for previous value in the running average when gusting
        )
        STORM_BASELINE_VAL = (
            BASELINE_VAL * 2
        )  # Baseline power level for the wind simulation when storming
        STORM_MIN_VAL = 0  # Minimum power level available when storming
        STORM_MAX_VAL = 300  # Maximum power level available when storming
        STORM_MAX_DEVIATION = (
            100  # Maximum deviation from the baseline power level when storming
        )
        STORM_FILTER_WEIGHT = (
            0.75  # Weight for previous value in the running average when storming
        )

    class AllocConsts:
        INIT_VAL = 0.0  # Initial value
        MAX_SLEW_RATE = 10.0  # Maximum slew rate for power allocation

    class WeatherStateMachine:
        class WeatherState(Enum):
            NORMAL = auto()
            GUSTING = auto()
            STORM = auto()

        class TransitionProbability:
            def __init__(
                self,
                population: list["Simulator.WeatherStateMachine.WeatherState"],
                weights: list[int],
            ):
                self.population = population
                self.weights = weights

        _TRANSITION_PROBABILITY = {
            WeatherState.NORMAL: TransitionProbability(
                list(WeatherState), [1000, 10, 1]
            ),
            WeatherState.GUSTING: TransitionProbability(
                list(WeatherState), [10, 1000, 1]
            ),
            WeatherState.STORM: TransitionProbability(list(WeatherState), [4, 1, 1000]),
        }

        def __init__(self):
            self._state = self.WeatherState.NORMAL

        def tick(self):
            choices = self._TRANSITION_PROBABILITY[self._state]
            self._state = random.choices(choices.population, choices.weights, k=1)[0]

        def is_normal(self):
            return self._state == self.WeatherState.NORMAL

        def is_gusting(self):
            return self._state == self.WeatherState.GUSTING

        def is_storm(self):
            return self._state == self.WeatherState.STORM

    def sim_states_factory(self, total_power: float, max_power_alloc: float) -> States:
        return States(
            {
                "total_power": State("SIM:WIND:TOTAL_POWER", total_power),
                "max_power_alloc": State("SIM:WIND:MAX_POWER_ALLOC", max_power_alloc),
            }
        )

    def __init__(self):
        self._sim_states = self.sim_states_factory(
            self.PowerConsts.INIT_VAL, self.AllocConsts.INIT_VAL
        )
        self._prev_sim_states = self._sim_states
        self._sim_setpoints = Setpoints(
            {"power_alloc": Setpoint("SIM:WIND:POWER_ALLOC_SETPOINT")}
        )
        self._weather_state_machine = self.WeatherStateMachine()

    def calculate_total_power(self) -> float:
        """
        Calculates the total power available to the wind powerplant.
        The total power is a lowpass filter of random values about
        the baseline, with occasional short gusts and rare
        longer-duration storms.
        """
        if self._weather_state_machine.is_normal():
            return self._calculate_total_power(
                current_power=self._prev_sim_states["total_power"],
                baseline=self.PowerConsts.BASELINE_VAL,
                min_val=self.PowerConsts.MIN_VAL,
                max_val=self.PowerConsts.MAX_VAL,
                max_deviation=self.PowerConsts.MAX_DEVIATION,
                filter_weight=self.PowerConsts.FILTER_WEIGHT,
            )
        elif self._weather_state_machine.is_gusting():
            return self._calculate_total_power(
                current_power=self._prev_sim_states["total_power"],
                baseline=self.PowerConsts.GUST_BASELINE_VAL,
                min_val=self.PowerConsts.GUST_MIN_VAL,
                max_val=self.PowerConsts.GUST_MAX_VAL,
                max_deviation=self.PowerConsts.GUST_MAX_DEVIATION,
                filter_weight=self.PowerConsts.GUST_FILTER_WEIGHT,
            )
        else:
            return self._calculate_total_power(
                current_power=self._prev_sim_states["total_power"],
                baseline=self.PowerConsts.STORM_BASELINE_VAL,
                min_val=self.PowerConsts.STORM_MIN_VAL,
                max_val=self.PowerConsts.STORM_MAX_VAL,
                max_deviation=self.PowerConsts.STORM_MAX_DEVIATION,
                filter_weight=self.PowerConsts.STORM_FILTER_WEIGHT,
            )

    def calculate_max_power_allocation(self, setpoint) -> float:
        """
        Calculates the maximum power allocatable, based on the desired setpoint.
        This includes non-idealities such as slew rate.
        """
        prev_alloc = self._prev_sim_states["max_power_alloc"]
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
        Starts the wind simulator.
        """
        # Wait for the wind IOC to start
        while ca.get("WIND:IS_RUNNING") is None:
            print("Waiting for the wind IOC to connect...")
            time.sleep(5)

        while not ca.put("WIND:IS_RUNNING", 1):
            time.sleep(5)
        print("Wind simulator started.")

    def tick(self):
        """
        Performs one tick of the wind simulation.
        """
        self._prev_sim_states = self._sim_states

        sim_setpoints = self._sim_setpoints.read_setpoints()

        self._weather_state_machine.tick()

        self._sim_states = self.sim_states_factory(
            self.calculate_total_power(),
            self.calculate_max_power_allocation(sim_setpoints["power_alloc"]),
        )
        self._sim_states.write_states()

    @staticmethod
    def clamp(number: float, lower: float, upper: float) -> float:
        return max(lower, min(number, upper))

    @staticmethod
    def _calculate_total_power(
        current_power: float,
        baseline: float,
        min_val: float,
        max_val: float,
        max_deviation: float,
        filter_weight: float,
    ) -> float:
        deviation = random.uniform(-max_deviation, max_deviation)
        total_power = (
            filter_weight * (current_power + deviation) + (1 - filter_weight) * baseline
        )
        return Simulator.clamp(total_power, min_val, max_val)
