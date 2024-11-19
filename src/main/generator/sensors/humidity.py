import os
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Any, Dict

import numpy as np
import logging


from .enums.battery import BatteryLevel
from .enums.status import StatusType
from .enums.humidity import HumiditySensorType
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
class HumidityCapacitiveSensor:
    type: HumiditySensorType = HumiditySensorType.CAPACITIVE
    unit: Units = Units.VOLT


@dataclass
class HumidityResistiveSensor:
    type: HumiditySensorType = HumiditySensorType.RESISTIVE
    unit: Units = Units.VOLT


class HumiditySensor(Sensor):
    _BATTERY_DECREASE_AMOUNT = 0.5

    def __init__(self, humidity_sensor_type):
        super().__init__()
        self.device_id = uuid.uuid1()
        self.device_type = "Humidity"
        self.unit = humidity_sensor_type.unit
        self.device_model = humidity_sensor_type.type.value
        self._battery_level = 100.0
        self.battery_status = BatteryLevel.FULL
        self.status = StatusType.ON
        self.location = (np.random.uniform(-90, 90), np.random.uniform(-180, 180))
        self.installation_date = datetime.now()
        self.last_maintenance = datetime.now()
        self.current_reading = self.read_data()
        self.log_file = self.log()
        self.group_id = np.random.randint(1, 30)
        self._decrease_battery()

    def _decrease_battery(self) -> None:
        if self._battery_level - self._BATTERY_DECREASE_AMOUNT > 0:
            self._battery_level -= self._BATTERY_DECREASE_AMOUNT
        else:
            self._battery_level = 0
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
            f"BatteryLevel: {self._battery_level},\n"
            f"Location: {self.location},\n"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DeviceId": str(self.device_id),
            "DeviceModel": str(self.device_model),
            "DeviceType": str(self.device_type),
            "Status": str(self.status),
            "CurrentReading": float(self.current_reading),
            "BatteryLevel": float(self._battery_level),
            "Location": str(self.location),
            "Timestamp": datetime.now().isoformat(),
        }

    def send_data(self) -> Dict[str, Any]:
        self.current_reading = self.read_data()
        return {
            "CurrentReading": self.current_reading,
            "Timestamp": self.timestamp.isoformat(),
            "DeviceId": str(self.device_id),
            "Location": self.location,
            "BatteryLevel": self._battery_level,
            "Status": self.status.value,
        }

    def read_data(self) -> float:
        if not hasattr(self, "timestamp"):
            self.timestamp = datetime.now()
            self.time_step = timedelta(minutes=5)
            self.base_humidity = np.random.uniform(30.0, 70.0)
            self.noise_level = 1.0
            self.anomaly_chance = 0.01

        self.timestamp += self.time_step

        hour_of_day = self.timestamp.hour + self.timestamp.minute / 60.0
        day_of_year = self.timestamp.timetuple().tm_yday

        daily_variation = 10 * np.sin(2 * np.pi * (hour_of_day + 4) / 24)  # Peak  04h

        seasonal_variation = 5 * np.sin(
            2 * np.pi * (day_of_year - 355) / 365
        )  # Peak en decemblre

        noise = np.random.normal(0, self.noise_level)

        if np.random.rand() < self.anomaly_chance:
            anomaly = np.random.uniform(-20, 20)
            logging.warning(
                f"Anomaly detected in sensor {self.device_id}: {anomaly:.2f}% change"
            )
        else:
            anomaly = 0

        humidity = (
            self.base_humidity + daily_variation + seasonal_variation + noise + anomaly
        )

        humidity = max(0, min(humidity, 100))

        return humidity

    def get_status(self) -> StatusType:
        return StatusType.ON

    def reset(self) -> bool:
        return True

    def log(self) -> str:
        log_directory = "./logs"
        log_file_path = f"{log_directory}/humidity_{self.device_id}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

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
