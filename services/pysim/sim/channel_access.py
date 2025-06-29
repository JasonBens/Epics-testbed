import epics
from typing import overload


def put(key: str, value: float) -> bool:
    """
    Puts the value to the given key in the EPICS channel access.
    Returns True if successful, False otherwise.
    """
    success = epics.caput(key, value)
    if success != 1:
        print(f"Failed to write value: {key}.")
        return False
    return True


@overload
def get(key: str) -> float | None: ...
@overload
def get(key: str, default_value: float) -> float: ...
def get(key: str, default_value: float | None = None) -> float | None:
    """
    Returns the value of the given key from the EPICS channel access.
    If the key does not exist or cannot be read, returns the default value if provided.
    """
    value = epics.caget(key)
    if value is None:
        if default_value is None:
            print(f"Warning: Unable to read key: {key}.")
            return value
        else:
            print(
                f"Warning: Unable to read key: {key}. Using default value: {default_value}."
            )
            return default_value
    return value


def get_setpoints_from_keys(keys: set) -> dict:
    """
    Returns a dictionary with the current setpoints of the control system.
    """
    setpoints = {key: epics.caget(key) for key in keys}
    missing_keys = [key for key, value in setpoints.items() if value is None]
    if missing_keys:
        print(f"Error: Unable to read the following keys: {', '.join(missing_keys)}.")
    return setpoints


def set_state_from_dict(state: dict[str, float]):
    """
    Sets the state of control system based on the passed dictionary.
    """
    result = {key: epics.caput(key, value) for key, value in state.items()}
    failed_puts = [key for key, success in result.items() if success != 1]
    if failed_puts:
        print(f"Failed to set the following keys: {', '.join(failed_puts)}.")
