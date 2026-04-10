import requests
import os
import json
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
from datetime import datetime
from azure.storage.blob import BlobServiceClient


def fetch_gtfs_feed(url):
    try:
        response = requests.get(url)
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed
    except Exception as e:
        print("Error fetching URL", {e})
        return None


def parse_feed(feed):
    return [MessageToDict(entity, preserving_proto_field_name=True) for entity in feed.entity]


def upload_to_azure(file_path, feed_type, filename):
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        print("AZURE_STORAGE_CONNECTION_STRING not set, skipping upload")
        return

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_name = f"{feed_type}/{filename}"
        blob_client = blob_service_client.get_blob_client(
            container="bronze",
            blob=blob_name
        )
        with open(file_path, "rb") as f:
            blob_client.upload_blob(f, overwrite=True)
        print(f"Uploaded {blob_name} to Azure Blob Storage")
    except Exception as e:
        print(f"Error uploading to Azure: {e}")


def save_feed(data, feed_type, output_dir):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir_final = os.path.join(output_dir, feed_type)
    os.makedirs(output_dir_final, exist_ok=True)

    filename = f"{feed_type}_{timestamp}.jsonl"
    file_path = os.path.join(output_dir_final, filename)

    with open(file_path, "w") as f:
        for record in data:
            f.write(json.dumps(record) + "\n")

    print(f"Saved {len(data)} records to {file_path}")

    upload_to_azure(file_path, feed_type, filename)


def run_all_feed(output_dir):
    FEED_URL = {
        "vehicle_positions": 'https://realtime.hsl.fi/realtime/vehicle-positions/v2/hsl',
        "trip_updates": 'https://realtime.hsl.fi/realtime/trip-updates/v2/hsl'
    }
    for feed_type, url in FEED_URL.items():
        print(f"extracting feed: {feed_type}")
        feed = fetch_gtfs_feed(url)
        if feed:
            data = parse_feed(feed)
            save_feed(data, feed_type, output_dir)


if __name__ == "__main__":
    output_dir = "/opt/airflow/data/raw"
    run_all_feed(output_dir)
