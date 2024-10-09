from confluent_kafka import Consumer
import logging

logging.basicConfig(level=logging.DEBUG)

conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "group1",
    "auto.offset.reset": "earliest",
}

consumer = Consumer(conf)
topic = "test"
consumer.subscribe([topic])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            logging.info("Waiting for message...")
        elif msg.error():
            logging.error(f"Error occurred: {msg.error()}")
        else:
            logging.info(
                "Consumed event from topic {topic}: key = {key:12} value = {value:12}".format(
                    topic=msg.topic(),
                    key=msg.key().decode("utf-8") if msg.key() else "None",
                    value=msg.value().decode("utf-8") if msg.value() else "None",
                )
            )
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
