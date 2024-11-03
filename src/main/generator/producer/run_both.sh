#!/bin/bash


sleep 5

run_producer() {
  for i in {1..10}; do
    poetry run python src/main/generator/producer/producer.py 
    sleep 1   
  done
}

run_producer 

wait

echo "Both scripts finished running."



