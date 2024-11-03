from enum import Enum


class TemperatureSensorType(Enum):
    THERMOMETER = "THERMOMETER"
    BIMETALLIC = "BIMETALLIC STRIPS"
    THERMOCOUPLE = "THERMOCOUPLE"
    THERMISTOR = "THERMISTOR"
    RTDS = "RTDS"
