import epics


class State:
    def __init__(self, key: str, value: float):
        self._key = key
        self._value = value
    
    def write_state(self) -> bool:
        """
        Writes state to the simulation.  Returns True on success, False otherwise.
        """
        success = epics.caput(self._key, self._value)
        if success != 1:
            print(f"Failed to write state: {self._key}.")
            return False
        return True


class States:
    def __init__(self, states: dict[str, State]) -> None:
        self._states = states

    def __getitem__(self, key):
        return self._states[key]._value

    def write_states(self) -> bool:
        """
        Writes states to the simulation.  Returns True on success, False otherwise.
        """
        success = [state.write_state() for state in self._states.values()]
        return all(success)
