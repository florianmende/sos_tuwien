import json
import googlemaps
from datetime import datetime
import os
from dotenv import load_dotenv
import argparse
from tqdm import tqdm

def calculate_travel_times(api_key, markets_data):
    """
    Calculates the travel time in seconds between all pairs of markets using pre-fetched coordinates.
    travel times from A -> B cna be different than from B -> A
    """
    gmaps = googlemaps.Client(key=api_key)
    results = {}

    valid_markets = [m for m in markets_data if m.get('latitude') is not None and m.get('longitude') is not None]

    for origin in tqdm(valid_markets):
        origin_id = origin['id']
        origin_name = origin['Name']
        origin_coords = (origin['latitude'], origin['longitude'])
        
        results[origin_id] = {}

        for destination in valid_markets:
            destination_id = destination['id']
            destination_name = destination['Name']
            destination_coords = (destination['latitude'], destination['longitude'])

            if origin_id == destination_id:
                results[origin_id][destination_id] = { "driving": 0, "walking": 0, "transit": 0 }
                continue

            modes = ["driving", "walking", "transit"]
            travel_times = {}

            for mode in modes:
                try:
                    now = datetime.now()
                    directions = gmaps.directions(origin_coords, destination_coords, mode=mode, departure_time=now)
                    
                    if directions:
                        travel_times[mode] = int(directions[0]['legs'][0]['duration']['value'])
                    else:
                        travel_times[mode] = None
                except googlemaps.exceptions.ApiError as e:
                    tqdm.write(f"API Error for {origin_name} to {destination_name} ({mode}): {e}")
                    travel_times[mode] = "API Error"
                except Exception as e:
                    tqdm.write(f"An unexpected error for {origin_name} to {destination_name} ({mode}): {e}")
                    travel_times[mode] = "Error"
            
            results[origin_id][destination_id] = travel_times
            
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        print("Error: GOOGLE_MAPS_API_KEY not found in .env file.")
    else:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                markets = json.load(f)
            
            travel_data = calculate_travel_times(api_key, markets)
            
            with open(args.output, "w", encoding='utf-8') as outfile:
                json.dump(travel_data, outfile, indent=4)
                
        except FileNotFoundError:
            print(f"Error: Input file not found at {args.input}")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {args.input}")