#!/usr/bin/env python3


from sensors.temperature import TemperatureSensor, TemperatureThermocoupleSensor


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
    data = s.send_data()
    for k, v in data.items():
        producer.produce(
            topic=topic, key=str(k), value=str(v), on_delivery=delivery_callback
        )
        producer.poll(1)

    producer.flush()
