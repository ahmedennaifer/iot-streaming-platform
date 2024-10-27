import logging
import os


import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Union

import numpy as np

from .enums.battery import BatteryLevel
from .enums.status import StatusType
from .enums.temperature import TemperatureSensorType
from .enums.units import Units
from sensors.sensor import Sensor

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


@dataclass
class TemperatureBimetallicSensor:
    type: TemperatureSensorType = TemperatureSensorType.BIMETALLIC
    unit: Units = Units.CELSIUS


@dataclass
class TemperatureThermometerSensor:
    type: TemperatureSensorType = TemperatureSensorType.THERMOMETER
    unit: Units = Units.CELSIUS


@dataclass
class TemperatureThermocoupleSensor:
    type: TemperatureSensorType = TemperatureSensorType.THERMOCOUPLE
    unit: Units = Units.VOLT


@dataclass
class TemperatureRTDSSensor:
    type: TemperatureSensorType = TemperatureSensorType.RTDS
    unit: Units = Units.OHM


@dataclass
class TemperatureThermistorSensor:
    type: TemperatureSensorType = TemperatureSensorType.THERMISTOR
    unit: Units = Units.OHM


class TemperatureSensor(Sensor):

    _BATTERY_LEVEL = 100
    _BATTERY_DECREASE_AMOUNT = 0.5

    def __init__(self, temperature_sensor_type):
        super().__init__()
        self.device_id = uuid.uuid1()
        self.device_type = temperature_sensor_type.type
        self.unit = temperature_sensor_type.unit
        self.device_model = ""
        self.battery_status = BatteryLevel.FULL
        self.status = StatusType.ON
        self.location = (np.random.uniform(-90, 90), np.random.uniform(-180, 180))
        self.installation_date = datetime.now()
        self.last_maintenance = datetime.now()
        self.current_reading = self.read_data()
        self.log_file = self.log()
        self.group_id = np.random.randint(1, 30)
        self._decrease_battery(self)

    @classmethod
    def _decrease_battery(cls, self) -> None:
        if cls._BATTERY_LEVEL - cls._BATTERY_DECREASE_AMOUNT > 0:
            cls._BATTERY_LEVEL -= cls._BATTERY_DECREASE_AMOUNT
        elif cls._BATTERY_LEVEL - cls._BATTERY_DECREASE_AMOUNT <= 0:
            cls._BATTERY_LEVEL = 0
            self.battery_status = BatteryLevel.EMPTY
            logging.critical(
                f"Sensor: {self.device_id} has NO battery! Charge immediately"
            )

    def __repr__(self) -> str:
        return (
            f"DeviceId: {self.device_id},\n"
            f"DeviceModel: {self.device_model},\n"
            f"DeviceType: {self.device_type},\n"
            f"Status: {self.status},\n"
            f"CurrentReading: {self.current_reading},\n"
            f"BatteryLevel: {TemperatureSensor._BATTERY_LEVEL},\n"
            f"Location: {self.location},\n"
        )

    def send_data(self) -> Dict[str, Any]:
        self.current_reading = np.random.uniform(1.0, 300)
        return {"Curent Reading": self.current_reading}

    def read_data(self) -> Union[int, float]:
        return np.random.uniform(1.0, 300)

    def get_status(self) -> StatusType:
        return StatusType.ON

    def reset(self) -> bool:
        return True
    

    def log(self) -> str:
        log_directory = "./logs"
        log_file_path = f"{log_directory}/temperature_{self.device_id}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

        os.makedirs(log_directory, exist_ok=True)

        existing_handlers = [
            h
            for h in logger.handlers
            if isinstance(h, logging.FileHandler) and h.baseFilename == log_file_path
        ]
        for handler in existing_handlers:
            logger.removeHandler(handler)
            handler.close()

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )

        logger.addHandler(file_handler)

        return log_file_path
    
  
            
            


