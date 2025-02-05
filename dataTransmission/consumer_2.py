from kafka import KafkaConsumer
import json
import os

# Kafka Configuration
KAFKA_TOPIC = "air-quality"
KAFKA_BROKER = "localhost:9092"
OUTPUT_FILE = "air_quality_data.json"  # File to store the data

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset="earliest",
    #enable_auto_commit=False,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    max_partition_fetch_bytes=10485760 
)

# Load existing data if the file already exists
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        try:
            stored_data = json.load(f)
            if not isinstance(stored_data, list):
                stored_data = []  # Ensure it's a list
        except json.JSONDecodeError:
            stored_data = []
else:
    stored_data = []

print("Waiting for messages...")

# Read messages from Kafka
for message in consumer:
    
    # print(f"📥 Received message: {message.value}")
    new_data = message.value  # This is the full JSON from the producer

    # 🔍 Debug: Print the full message received
    '''
    print("\n📥 Full message received from Kafka:")
    print(json.dumps(new_data, indent=4, ensure_ascii=False))
    '''

    # Store the new data in the list
    stored_data = new_data

    # Save updated data back to the file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(stored_data, f, ensure_ascii=False, indent=4)

    # Commit the offset manually after processing
    #consumer.commit()
    print(f"✅ Updated {OUTPUT_FILE} with {len(stored_data)} total records")
