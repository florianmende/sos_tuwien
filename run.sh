poetry run python3 ./src/find_solution.py \
    --algorithm ga --service_time 30 \
    --places_file data/places.json \
    --travel_times data/travel_times.json \
    --days 3 \
    --params best_params.json