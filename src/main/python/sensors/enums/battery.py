from enum import Enum
import numpy as np


class BatteryLevel(Enum):
    FULL = 100.0
    EMPTY = 0.0
    WORKING = 50.0
