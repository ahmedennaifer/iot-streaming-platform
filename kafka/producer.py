#!/usr/bin/env python3


from confluent_kafka import Producer
import logging

logging.basicConfig(level=logging.DEBUG)

conf = {"bootstrap.servers": "kafka:9092"}


def delivery_callback(err, msg):
    if err:
        logging.error(f"ERROR: Message failed delivery: {err}")
    else:
        key = msg.key() if msg.key() is not None else "None"
        value = msg.value() if msg.value() is not None else "None"
        logging.info(
            f"Produced event to topic {msg.topic()}: key = {str(key):12} value = {str(value):12}"
        )


producer = Producer(conf)
topic = "test"

example_message = {"test1": "message1", "test2": "message2", "test3": "message3"}


while True:
    for k, v in example_message.items():
        producer.produce(topic, k, v, callback=delivery_callback)
        producer.poll(1)

producer.flush()
