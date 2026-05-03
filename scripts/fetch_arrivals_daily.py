import os
import requests
import json
from datetime import datetime, timedelta

def main():
    parish_id = os.getenv("parish_id", "151006")  # string
    print("Fetching stops from API...")
    response = requests.get("https://api.carrismetropolitana.pt/v2/stops")
    response.raise_for_status()
    all_stops = response.json()

    # Filter active stops where parish_id matches (as string)
    filtered_stops = [
        stop for stop in all_stops
        if str(stop.get("parish_id")) == parish_id and stop.get("operational_status") == "active"
    ]
    stop_ids = [stop["id"] for stop in filtered_stops]
    print(f"Found {len(stop_ids)} active stops for parish_id {parish_id}")

    if not stop_ids:
        print("No stops found. Exiting.")
        return

    # Fetch arrivals for previous day
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    arrivals_by_stop = {}

    for stop_id in stop_ids:
        url = f"https://api.carrismetropolitana.pt/v2/arrivals/by_stop/{stop_id}"
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    arrivals_by_stop[stop_id] = data
                print(f"Stop {stop_id}: {len(data)} arrivals")
            else:
                print(f"Stop {stop_id} -> HTTP {resp.status_code}")
        except Exception as e:
            print(f"Error on stop {stop_id}: {e}")

    # Save output (overwrites previous day's file)
    output_data = {
        "extraction_date": yesterday,
        "parish_id": parish_id,
        "arrivals": arrivals_by_stop
    }

    os.makedirs("data", exist_ok=True)
    output_file = "data/arrivals_fernao_ferro.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Saved to {output_file} | Stops with arrivals: {len(arrivals_by_stop)}")

if __name__ == "__main__":
    main()
