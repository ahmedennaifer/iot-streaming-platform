from .temperature import TemperatureSensor, TemperatureThermistorSensor

while TemperatureSensor._BATTERY_LEVEL > 0:
    s = TemperatureSensor(TemperatureThermistorSensor())
    print(s)
