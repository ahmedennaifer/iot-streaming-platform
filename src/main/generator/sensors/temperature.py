import logging
import os

import uuid

from dataclasses import dataclass
from datetime import datetime, timedelta
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
    _BATTERY_DECREASE_AMOUNT = 0.5

    def __init__(self, temperature_sensor_type):
        super().__init__()
        self.device_id = uuid.uuid1()
        self.device_type = temperature_sensor_type.type.value
        self.unit = temperature_sensor_type.unit
        self.device_model = ""
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
        elif self._battery_level - self._BATTERY_DECREASE_AMOUNT <= 0:
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
            "DeviceId": str(self.device_id)
            if isinstance(self.device_id, uuid.UUID)
            else self.device_id,
            "DeviceModel": str(self.device_model),
            "DeviceType": str(self.device_type),
            "Status": str(self.status),
            "CurrentReading": float(self.current_reading),
            "BatteryLevel": float(self._battery_level),
            "Location": str(self.location),
            "Timestamp": datetime.now().isoformat(),
        }

    def send_data(self) -> Dict[str, Any]:
        self.current_reading = np.random.uniform(1.0, 300)
        return {"Curent Reading": self.current_reading}

    def read_data(self) -> float:
        if not hasattr(self, "timestamp"):
            self.timestamp = datetime.now()
            self.time_step = timedelta(minutes=5)
            self.base_temperature = np.random.uniform(15.0, 25.0)
            self.noise_level = 0.5
            self.anomaly_chance = 0.01

        self.timestamp += self.time_step

        hour_of_day = self.timestamp.hour + self.timestamp.minute / 60.0
        day_of_year = self.timestamp.timetuple().tm_yday

        daily_variation = 10 * np.sin(
            2 * np.pi * (hour_of_day - 6) / 24
        )  # On simule les variations avec une fonctions sinusoidale, qui peak a 12h

        seasonal_variation = 5 * np.sin(
            2 * np.pi * (day_of_year - 172) / 365
        )  # Pas sur que c'est très utile, mais variation qui peak en Juin

        noise = np.random.normal(0, self.noise_level)  # bruit

        if np.random.rand() < self.anomaly_chance:
            anomaly = np.random.uniform(-15, 15)  # Simulation d'anomalies
            logging.warning(
                f"Anomaly detected in sensor {self.device_id}: {anomaly:.2f}° change"
            )
        else:
            anomaly = 0

        temperature = (
            self.base_temperature
            + daily_variation
            + seasonal_variation
            + noise
            + anomaly
        )

        temperature = max(-50, min(temperature, 60))

        return temperature

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
