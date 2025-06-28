import time
import channel_access as ca


class Simulator:
    def __init__(self):
        self._state_of_charge = 0.0

    def get_available_power(self) -> float:
        return ca.get("SIM:BATTERY:AVAILABLE_POWER", 0)

    def tick(self):
        self._state_of_charge += self.get_available_power() / 1000.0
        ca.put("SIM:BATTERY:STATE_OF_CHARGE", self._state_of_charge)

    def start(self):
        """
        Starts the battery simulator.
        """
        # Wait for the battery IOC to start
        while ca.get("BATTERY:IS_RUNNING") is None:
            print("Waiting for the battery IOC to connect...")
            time.sleep(5)

        while not ca.put("BATTERY:IS_RUNNING", 1):
            time.sleep(5)
        print("Battery simulator started.")
