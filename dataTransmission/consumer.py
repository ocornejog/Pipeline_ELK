from kafka import KafkaConsumer
import json

# Kafka Consumer configuration
consumer = KafkaConsumer(
    "air-quality",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("Waiting for messages...")
for message in consumer:
    print(f"Received: {message.value}")
