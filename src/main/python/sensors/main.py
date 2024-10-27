from temperature import TemperatureSensor, TemperatureThermistorSensor, TemperatureBimetallicSensor, TemperatureThermocoupleSensor 
from random import choice

sensor_types = [TemperatureThermocoupleSensor, TemperatureThermistorSensor, TemperatureBimetallicSensor]

while TemperatureSensor._BATTERY_LEVEL > 0:
    for i in range(10):
        i = TemperatureSensor(choice(sensor_types))
        print(i)
