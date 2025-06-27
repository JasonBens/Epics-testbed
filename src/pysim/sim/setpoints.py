import epics


class Setpoint:
    def __init__(self, key: str):
        self._key = key

    def read_setpoint(self) -> float | None:
        value = epics.caget(self._key)
        if value is None:
            print(f"Failed to read setpoint: {self._key}.")
        return value


class Setpoints:
    def __init__(self, setpoints: dict[str, Setpoint]):
        self._setpoints = setpoints

    def read_setpoints(self) -> dict[str, float | None]:
        return {
            key: setpoint.read_setpoint() for key, setpoint in self._setpoints.items()
        }
