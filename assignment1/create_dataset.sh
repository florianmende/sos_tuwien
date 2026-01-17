set -e

echo "--- Step 1: Enriching raw_data.json with IDs and coordinates ---"
poetry run python -m src.prepare_data.prepare_places --input ./data/raw_data.json --output ./data/places.json

echo ""
echo "--- Step 2: Calculating travel times from places.json ---"
poetry run python -m src.prepare_data.fetch_travel_time --input ./data/places.json --output ./data/travel_times.json