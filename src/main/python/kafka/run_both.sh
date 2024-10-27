#!/bin/bash


sleep 5

run_producer() {
  for i in {1..10}; do
    poetry run python src/main/python/kafka/producer.py 
    sleep 1   
  done
}

run_consumer() {
poetry run python src/main/python/kafka/consumer.py
}

run_producer &
run_consumer &

wait

echo "Both scripts finished running."



