#!/usr/bin/env python3


import json
import uuid
from sensors.temperature import TemperatureSensor, TemperatureThermocoupleSensor
from sensors.enums.temperature import TemperatureSensorType


from confluent_kafka import Producer
import logging


logging.basicConfig(level=logging.DEBUG)

conf = {"bootstrap.servers": "kafka:9092"}


def delivery_callback(err, msg):
    if err:
        logging.error(f"ERROR: Message failed delivery: {err}")
    else:
        key = msg.key().decode("utf-8") if msg.key() else "None"
        value = msg.value().decode("utf-8") if msg.value() else "None"
        logging.info(
            f"Produced event to topic {msg.topic()}: key = {key} value = {value}"
        )


producer = Producer(conf)
topic = "test"
s = TemperatureSensor(TemperatureThermocoupleSensor)


while True:
    readings = s.to_dict()
    v = json.dumps(readings).encode('utf-8')
    
    producer.produce(
            topic=topic, key=None, value=v, on_delivery=delivery_callback
        )
    producer.poll(1)
    producer.flush()
