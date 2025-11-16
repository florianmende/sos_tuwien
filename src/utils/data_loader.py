import json


def load_market_data(places_file, travel_times_file, mode="transit"):
    """
    Load and validate market and travel time data.
    
    Args:
        places_file: JSON file with market metadata
        travel_times_file: JSON with directed travel times
        mode: "transit", "walking", or "driving"
    
    Returns:
        markets, travel_times: Processed data structures with integer keys
    """
    with open(places_file, 'r') as f:
        markets_raw = json.load(f)
    
    with open(travel_times_file, 'r') as f:
        travel_times_raw = json.load(f)
    
    # Markets use string keys (for compatibility)
    markets = {str(m["id"]): m for m in markets_raw}
    
    # Convert time strings to minutes since midnight
    for market in markets.values():
        opens_h, opens_m = map(int, market["Opens"].split(":"))
        closes_h, closes_m = map(int, market["Closes"].split(":"))
        market["opens_minutes"] = opens_h * 60 + opens_m
        market["closes_minutes"] = closes_h * 60 + closes_m
    
    # Convert nested string keys to integers for travel_times
    travel_times = {
        int(from_id): {
            int(to_id): tt.get(mode, 0) // 60
            for to_id, tt in destinations.items()
        }
        for from_id, destinations in travel_times_raw.items()
    }
    
    return markets, travel_times
