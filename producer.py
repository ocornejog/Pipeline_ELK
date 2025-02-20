from kafka import KafkaProducer
import requests
import json
import time
import csv
import io
from datetime import datetime, timedelta
from unidecode import unidecode
import pandas as pd
import os

# Configuration
BASE_URL = "https://files.data.gouv.fr/lcsqa/concentrations-de-polluants-atmospheriques-reglementes/temps-reel/2025"
KAFKA_TOPIC = "air-quality"
KAFKA_BROKER = "localhost:9092"
CHUNK_SIZE = 1000  # Number of records per message

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    max_request_size=1048576000  # 1000MB
)

def get_csv_files():
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        # Parse the HTML to find CSV files
        files = [line for line in response.text.split('\n') if 'FR_E2_' in line and '.csv' in line]
        # Extract filenames and create full URLs
        csv_files = []
        for line in files:
            try:
                filename = line.split('"')[1]  # Try to extract filename between quotes
                csv_files.append(f"{BASE_URL}/{filename}")
            except (IndexError, ValueError) as e:
                print(f"Error parsing line: {line}")
                continue
        return csv_files
    return []

def csv_to_json(csv_data):
    csv_reader = csv.DictReader(io.StringIO(csv_data), delimiter=';')
    return list(csv_reader)

def normalize_json(data):
    normalized_data = []
    for item in data:
        normalized_item = {unidecode(key): unidecode(value) for key, value in item.items()}
        normalized_data.append(normalized_item)
    return normalized_data

def process_file(url):
    if "FR_E2_2025-02" not in url:
        return 0
        
    print(f"Processing file: {url}")
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error downloading file {url}: Status code {response.status_code}")
            return 0
            
        # Set the correct encoding for the response content
        response.encoding = 'utf-8'
        
        # Convert CSV to JSON and normalize the data
        json_data = csv_to_json(response.text)
        normalized_data = normalize_json(json_data)
        
        total_records = len(normalized_data)
        chunk_number = 0
        total_chunks = (total_records + CHUNK_SIZE - 1) // CHUNK_SIZE
        
        # Send data in chunks
        for i in range(0, total_records, CHUNK_SIZE):
            chunk_data = normalized_data[i:i + CHUNK_SIZE]
            
            message = {
                "filename": os.path.basename(url),
                "chunk_number": chunk_number,
                "total_chunks": total_chunks,
                "data": chunk_data
            }
            
            producer.send(KAFKA_TOPIC, value=message["data"])
            print(f"Sent chunk {chunk_number + 1}/{total_chunks} for {url}")
            chunk_number += 1
        
        producer.flush()
        return total_records
            
    except Exception as e:
        print(f"Error processing file {url}: {str(e)}")
        return 0

def chunk_data(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

def main():
    processed_files = set()
    
    while True:
        try:
            csv_files = get_csv_files()
            current_time = datetime.now()
            
            csv_files.sort()
            
            for file_url in csv_files:
                if file_url not in processed_files:
                    total_records = process_file(file_url)
                    
                    if total_records > 0:
                        processed_files.add(file_url)
                        print(f"✅ Processed {total_records} records from {file_url}")
                    
            print(f"Processed {len(processed_files)} files. Waiting for new files...")
            time.sleep(60)  # Wait for 1 minute before checking for new files
            
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    main()