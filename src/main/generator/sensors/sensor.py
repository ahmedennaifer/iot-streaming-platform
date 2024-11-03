from random import choice
from datetime import datetime
from abc import ABC, abstractmethod

from .enums.status import StatusType



from typing import Any, Union, Dict

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# TODO : check logging issue -> only info gets logged


class Sensor(ABC):
    def __init__(self):
        self.device_id = None
        self.device_type = None
        self.status = choice(list(StatusType))
        self.battery_level = 100
        self.location = None
        self.installation_date = datetime.now()
        self.last_maintenance = None
        self.device_model = None
        self.current_reading = None
        self.unit = None
        self.log_file = None

    @abstractmethod
    def send_data(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def read_data(self) -> Union[int, float]:
        pass

    @abstractmethod
    def get_status(self) -> StatusType:
        pass

    @abstractmethod
    def reset(self) -> bool:
        pass

    @abstractmethod
    def log(self) -> str:
        pass
