import requests
import os
import json
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
from datetime import datetime


def fetch_gtfs_feed(url):
    ''' Fetches GTFS Realtime feed from HSL and parses it into a FeedMessage '''
    try:
        response = requests.get(url)
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed
    except Exception as e:
        print("Error fetching URL", {e})
        return None


def parse_feed(feed):
    ''' Parses a GTFS FeedMessage into a list of dicts using MessageToDict '''
    return [MessageToDict(entity, preserving_proto_field_name=True) for entity in feed.entity]


def save_feed(data, feed_type, output_dir):
    ''' Saves parsed GTFS data to a timestamped JSON file '''
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{feed_type}_{timestamp}.json")

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Saved {len(data)} records to {file_path}")


def extract_and_save(url, feed_type, output_dir):
    feed = fetch_gtfs_feed(url)
    data = parse_feed(feed)
    save_feed(data, feed_type, output_dir)


def run_all_feed(output_dir):
    FEED_URL = {
        "vehicle_position": 'https://realtime.hsl.fi/realtime/vehicle-positions/v2/hsl',
        "trip_updates": 'https://realtime.hsl.fi/realtime/trip-updates/v2/hsl'
    }
    for feed_type, url in FEED_URL.items():
        print(f"extracting feed: {feed_type}")
        feed = fetch_gtfs_feed(url)
        if feed:
            data = parse_feed(feed)
            save_feed(data, feed_type, output_dir)


# Only run when i execute the script
if __name__ == "__main__":
    output_dir = "../data/raw"
    run_all_feed(output_dir)
