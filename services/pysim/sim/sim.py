import time
import solar
import wind
import battery
import channel_access as ca

class Simulator:
    def __init__(self) -> None:
        self.solar_simulator = solar.Simulator()
        self.wind_simulator = wind.Simulator()
        self.battery_simulator = battery.Simulator()

    def start(self):
        self.solar_simulator.start()
        self.wind_simulator.start()
        self.battery_simulator.start()
        while ca.get("SIM:IS_RUNNING") is None:
            print("Waiting for the pysim IOC to connect...")
            time.sleep(5)
        while ca.put("SIM:IS_RUNNING", 1) is None:
            time.sleep(5)
        print("Simulation started.")

    def tick(self):
        self.solar_simulator.tick()
        self.wind_simulator.tick()
        self.battery_simulator.tick()
        
def main():
    simulator = Simulator()
    simulator.start()
    while True:
        simulator.tick()
        time.sleep(0.5)

if __name__ == "__main__":
    main()
