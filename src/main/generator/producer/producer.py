#!/usr/bin/env python3


import json
import time

from src.main.generator.sensors.temperature import (
    TemperatureBimetallicSensor,
    TemperatureRTDSSensor,
    TemperatureSensor,
    TemperatureThermistorSensor,
    TemperatureThermocoupleSensor,
)


from confluent_kafka import Producer
import logging


logging.basicConfig(level=logging.DEBUG)

conf = {"bootstrap.servers": "kafka:9092"}


producer = Producer(conf)
topic = "test"
devices = [
    TemperatureSensor(TemperatureThermocoupleSensor()),
    TemperatureSensor(TemperatureBimetallicSensor()),
    TemperatureSensor(TemperatureThermistorSensor()),
    TemperatureSensor(TemperatureRTDSSensor()),
]


def delivery_callback(err, msg):
    if err:
        logging.error(f"ERROR: Message failed delivery: {err}")
    else:
        key = msg.key().decode("utf-8") if msg.key() else "None"
        value = msg.value().decode("utf-8") if msg.value() else "None"
        logging.info(
            f"Produced event to topic {msg.topic()}: key = {key} value = {value}"
        )


while True:
    for device in devices:
        device.current_reading = device.read_data()
        device._decrease_battery()

        readings = device.to_dict()
        v = json.dumps(readings).encode("utf-8")

        producer.produce(
            topic=topic,
            key=str(device.device_id),
            value=v,
            on_delivery=delivery_callback,
        )

    producer.poll(10)
    producer.flush()

    time.sleep(1)

