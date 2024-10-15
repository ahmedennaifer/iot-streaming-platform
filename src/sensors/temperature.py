import logging
import uuid
import numpy as np
import os

from datetime import datetime
from random import choice

from enums.units import Units
from enums.battery import BatteryLevel
from enums.status import StatusType
from enums.temperature import TemperatureSensorType
from sensor import Sensor


# TODO :  add param in sensor class, to define attributes, ie: profile1 : battery level full, etc

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class TemperatureSensor(Sensor):
    def __init__(self):
        super().__init__()
        self.device_id = uuid.uuid1()
        logger.debug(f"Starting device : {self.device_id}, TIME : {datetime.now()}")
        self.device_type = choice(list(TemperatureSensorType))
        self.device_model = ""
        self.status = StatusType.ON
        self.battery_level = BatteryLevel.FULL
        self.location = (np.random.uniform(-90, 90), np.random.uniform(-180, 180))
        self.installation_date = datetime.now()
        self.last_maintenance = datetime.now()
        self.current_reading = self.read_data()
        self.unit = Units.CELSIUS
        self.log_file = self.log()
        self.group_id = np.random.randint(1, 30)
        logger.info(
            f"Device {self.device_id} started successfully. Time took to start : {datetime.now() - self.installation_date}"
        )

    def __repr__(self) -> str:
        return (
            f"DeviceId: {self.device_id},\n"
            f"DeviceModel: {self.device_model},\n"
            f"DeviceType: {self.device_type},\n"
            f"Status: {self.status},\n"
            f"installation_date: {self.installation_date},\n"
            f"CurrentReading: {self.current_reading},\n"
            f"BatteryLevel: {self.battery_level},\n"
            f"Location: {self.location},\n"
            f"LogFile: {self.log_file}"
        )

    def send_data(self):
        return True

    def read_data(self):
        return {"test": "test"}

    def get_status(self) -> StatusType:
        return StatusType.ON

    def reset(self) -> bool:
        return True

    def log(self) -> str:
        log_directory = "./logs"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        log_file_path = f"{log_directory}/temperature_{self.device_id}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                logger.removeHandler(handler)
                handler.close()
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )

        logger.addHandler(file_handler)

        return log_file_path
