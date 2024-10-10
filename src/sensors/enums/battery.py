from enum import Enum
import numpy as np


class BatteryLevel(Enum):
    FULL = 100.0
    EMPTY = 0.0
    RANDOM = np.random.uniform(1, 99)
