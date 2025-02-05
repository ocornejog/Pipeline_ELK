from kafka import KafkaProducer
import requests
import json
import time

# API URL
#To get the first ten results
# API_URL = "https://data.ratp.fr/api/explore/v2.1/catalog/datasets/qualite-de-lair-mesuree-dans-la-station-nation-rer-a0/records"

#To get all results in a json format (this could be changed to another formats such as csv, parquet, xlsx and others)
API_URL = "https://data.ratp.fr/api/explore/v2.1/catalog/datasets/qualite-de-lair-mesuree-dans-la-station-nation-rer-a0/exports/json"

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

while True:
    try:
        response = requests.get(API_URL)
        
        if response.status_code == 200:
            data = response.json()
            data_size = len(json.dumps(data).encode("utf-8"))  # Calculate size in bytes
            
            print(f"Fetched {len(data)} records from API. Total size: {data_size / 1024} KB")

            if data_size > 10000000:  # 10 MB
                print("⚠️ WARNING: JSON data exceeds 10 MB!")
            
            # Check if "results" key exists in API response
            # Uncomment this lines for API-URL with /records endpoint
            ''' 
            if "results" in data:
                for record in data["results"]:
                    producer.send(KAFKA_TOPIC, record)
                    print(f"Sent: {record}")
            else:
                print("Warning: 'results' key not found in API response.")
            '''
            if isinstance(data, list) and len(data) >= 2:
                print("First two elements being sent:")
                print(json.dumps(data[:2], indent=4, ensure_ascii=False))
            
            # Uncomment this lines for API-URL with /exports/json endpoint
            # Send the entire JSON response as one Kafka message
            producer.send(KAFKA_TOPIC, data)
            print(f"✅ Sent {len(data)} records to Kafka")

        else:
            print(f"❌ Error fetching data: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Wait 300 seconds before the next request
    time.sleep(300)
