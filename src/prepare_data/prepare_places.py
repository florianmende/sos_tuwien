import json
import argparse
import re
import requests
from tqdm import tqdm

def get_coordinates_from_url(url):
    """
    Extracts latitude and longitude from a Google Maps URL.
    """
    try:
        if "goo.gl" in url or "g.page" in url or "maps.app.goo.gl" in url:
            response = requests.head(url, allow_redirects=True)
            url = response.url

        # Regex to find latitude and longitude in the URL
        patterns_to_try = [
            r"@(-?\d+\.\d+),(-?\d+\.\d+)",           # Standard format: @lat,lng
            r"/search/(-?\d+\.\d+),.*?(-?\d+\.\d+)",  # /search/lat,+lng
        ]

        for pattern in patterns_to_try:
            match = re.search(pattern, url)
            if match:
                latitude, longitude = match.groups()
                return (float(latitude), float(longitude))
    except requests.RequestException as e:
        print(f"Could not resolve shortened URL {url}. Error: {e}")
        return None
    
    print(f"Could not extract coordinates from URL: {url}")
    return None

def enrich_data(input_file, output_file):
    """
    Reads a JSON file, adds unique IDs, fetches geographic coordinates,
    and saves the enriched data to a new file.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_file}")
        return

    enriched_data = []
    for i, item in enumerate(tqdm(data)):
        
        item['id'] = i + 1
        
        coords = get_coordinates_from_url(item['Map'])
        if coords:
            item['latitude'] = coords[0]
            item['longitude'] = coords[1]
        else:
            item['latitude'] = None
            item['longitude'] = None
        
        enriched_data.append(item)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error writing to file {output_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    
    args = parser.parse_args()
    
    enrich_data(args.input, args.output)