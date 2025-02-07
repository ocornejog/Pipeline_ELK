from kafka import KafkaProducer
import requests
import json
import time
import csv
import io
from datetime import datetime, timedelta
from unidecode import unidecode

# API URLs
BASE_URL = "https://www.geodair.fr/api-ext"
EXPORT_URL = f"{BASE_URL}/MoyJ/export"
DOWNLOAD_URL = f"{BASE_URL}/download"

# API Key
API_KEY = "KpwHhI3B6pxFRmm695biio8rV1huKLFt"

# Polluants list (from the PDF)
# POLLUANTS = ["01", "03", "04", "08", "12", "19", "24", "39", "80", "82", "87", "P6", "V4"]  # Add all polluants from the PDF
POLLUANTS = ["01"]  # Add all polluants from the PDF

# Kafka Configuration
KAFKA_TOPIC = "air-quality"
KAFKA_BROKER = "localhost:9092"

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    max_request_size=10485760
)

print(f"Starting producer... Sending data to topic: {KAFKA_TOPIC}")

def get_yesterday_date():
    return (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")

def fetch_container_ids(date):
    container_ids = []
    headers = {"apikey": API_KEY}
    for polluant in POLLUANTS:
        retries = 1
        while retries > 0:
            response = requests.get(f"{EXPORT_URL}?date={date}&polluant={polluant}", headers=headers)
            if response.status_code == 200:
                container_ids.append(response.text.strip())
                break
            elif response.status_code == 429:
                print(f"❌ Rate limit exceeded for polluant {polluant}. Retrying...")
                time.sleep(2 ** (5 - retries))  # Exponential backoff
                retries -= 1
            else:
                print(f"❌ Error fetching container ID for polluant {polluant}: {response.status_code}")
                print(f"Response content: {response.content}")
                break
    return container_ids

def download_csv(container_id):
    headers = {"apikey": API_KEY}
    response = requests.get(f"{DOWNLOAD_URL}?id={container_id}", headers=headers)
    if response.status_code == 200:
        return response.content.decode("utf-8")
    else:
        print(f"❌ Error downloading CSV for container ID {container_id}: {response.status_code}")
        print(f"Response content: {response.content}")
        return None

def csv_to_json(csv_data):
    csv_reader = csv.DictReader(io.StringIO(csv_data), delimiter=';')
    return list(csv_reader)

def normalize_json(data):
    normalized_data = []
    for item in data:
        normalized_item = {unidecode(key): unidecode(value) for key, value in item.items()}
        normalized_data.append(normalized_item)
    return normalized_data

while True:
    try:
        yesterday_date = get_yesterday_date()
        container_ids = fetch_container_ids(yesterday_date)
        
        all_data = []
        for container_id in container_ids:
            csv_data = download_csv(container_id)
            if csv_data:
                json_data = csv_to_json(csv_data)
                normalized_json_data = normalize_json(json_data)
                all_data.extend(normalized_json_data)
        
        if all_data:
            data_size = len(json.dumps(all_data).encode("utf-8"))  # Calculate size in bytes
            print(f"Fetched data for {len(container_ids)} polluants. Total size: {data_size / 1024} KB")

            if data_size > 10000000:  # 10 MB
                print("⚠️ WARNING: JSON data exceeds 10 MB!")

            # Print the first two elements of the JSON data
            print("First two elements of the JSON data to be sent to Kafka:")
            print(json.dumps(all_data[:2], indent=2))

            producer.send(KAFKA_TOPIC, all_data)
            print(f"✅ Sent data to Kafka")

        else:
            print("❌ No data fetched")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Wait 86400 seconds (1 day) before the next request
    time.sleep(86400)