#!/bin/bash

poetry run python3 ./src/run.py \
  --algorithm all \
  --service_time 30 \
  --places_file data/places.json \
  --travel_times_file data/travel_times.json
