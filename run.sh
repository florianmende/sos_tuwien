#!/bin/bash

poetry run python3 ./src/run.py \
  --algorithm ga \
  --service_time 30 \
  --places_file data/places.json \
  --travel_times_file data/travel_times.json \
  --days 1
