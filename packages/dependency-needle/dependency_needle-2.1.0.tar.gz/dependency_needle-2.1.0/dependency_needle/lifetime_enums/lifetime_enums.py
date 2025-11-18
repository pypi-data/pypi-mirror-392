from enum import Enum


class LifeTimeEnums(Enum):
    """Life time enums used when registering an interface."""

    # Same object for each dependant class across a single request.
    SCOPED = "scoped"
    # New object for each dependant class.
    TRANSIENT = "transient"
    # Same object for each dependant class for any request.
    SINGLETON = "singleton"
