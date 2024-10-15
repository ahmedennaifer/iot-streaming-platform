#!/bin/bash


sleep 5

run_producer() {
  for i in {1..10}; do
    poetry run kafka/producer.py   
    sleep 1   
  done
}

run_consumer() {
  poetry run kafka/consumer.py   
}

run_producer &
run_consumer &

wait

echo "Both scripts finished running."
