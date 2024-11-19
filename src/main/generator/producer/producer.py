#!/usr/bin/env python3


import json
import time
import logging

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer

from src.main.generator.sensors.temperature import (
    TemperatureBimetallicSensor,
    TemperatureRTDSSensor,
    TemperatureSensor,
    TemperatureThermistorSensor,
    TemperatureThermocoupleSensor,
)

from src.main.generator.sensors.humidity import (
    HumidityCapacitiveSensor,
    HumidityResistiveSensor,
    HumiditySensor,
)

logging.basicConfig(level=logging.DEBUG)

conf = {"bootstrap.servers": "kafka:9092"}

admin = AdminClient(conf)

topics = [
    NewTopic("temperature", num_partitions=1, replication_factor=1),
    NewTopic("humidity", num_partitions=1, replication_factor=1),
]

devices = [
    TemperatureSensor(TemperatureThermocoupleSensor()),
    TemperatureSensor(TemperatureBimetallicSensor()),
    TemperatureSensor(TemperatureThermistorSensor()),
    TemperatureSensor(TemperatureRTDSSensor()),
    HumiditySensor(HumidityCapacitiveSensor()),
    HumiditySensor(HumidityResistiveSensor()),
]

try:
    fs = admin.create_topics(topics)
    for topic, f in fs.items():
        try:
            f.result()
            logging.info(f"Topic '{topic}' created successfully.")
        except Exception as e:
            logging.warning(f"Failed to create topic '{topic}': {e}")
except Exception as e:
    logging.error(f"Failed to create topics: {e}")


def delivery_callback(err, msg):
    if err:
        logging.error(f"Message failed delivery: {err}")
    else:
        key = msg.key().decode("utf-8") if msg.key() else "None"
        value = msg.value().decode("utf-8") if msg.value() else "None"
        logging.info(
            f"Produced event to topic '{msg.topic()}': key = {key} value = {value}"
        )


producer = Producer(conf)

while True:
    for device in devices:
        device.current_reading = device.read_data()
        device._decrease_battery()

        readings = device.to_dict()
        value = json.dumps(readings).encode("utf-8")

        if isinstance(device, TemperatureSensor):
            topic = "temperature"
        elif isinstance(device, HumiditySensor):
            topic = "humidity"
        else:
            continue

        producer.produce(
            topic=topic,
            key=str(device.device_id),
            value=value,
            callback=delivery_callback,
        )

        producer.poll(0)

    time.sleep(1)
