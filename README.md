
# Kafka Producer and Consumer Setup

This guide will help you set up and run Kafka **Producer** and **Consumer** using Docker and Python, including the necessary verifications for Kafka topic creation and container functionality.

## Prerequisites

Make sure you have the following installed:

- **Docker Desktop** (for Windows)
- **Docker Compose**
- **Python 3.6+**
- **Kafka Python Client** (`kafka-python`)
- **requests** library for API calls

## Steps to Execute

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Set Up Docker Containers

1. **Navigate to your project directory** where `docker-compose.yml` is located.

2. **Start the Docker containers**:

```bash
docker-compose up -d
```

This will start Kafka and Zookeeper containers in detached mode.

3. **Verify Kafka and Zookeeper Containers are Running**

Run the following command to verify that both containers are up and running:

```bash
docker ps
```

You should see both **zookeeper** and **kafka** containers running.

4. **Verify Kafka Broker**

You can check if the Kafka broker is running properly by looking at the logs:

```bash
docker-compose logs kafka
```

### 3. Create Kafka Topic

1. **Create the Kafka Topic** for your Producer and Consumer to use. Run the following command to create the topic (`air-quality` in this case):

```bash
docker exec -it <kafka-container-name> kafka-topics.sh --create --topic air-quality --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092
```

Replace `<kafka-container-name>` with the actual container name of your Kafka container (you can find it by running `docker ps`).

In this case:

```bash
docker exec -it kafka kafka-topics.sh --create --topic air-quality --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092
```

2. **Verify Kafka Topic**

After creating the topic, verify that it was created successfully by running:

```bash
docker exec -it <kafka-container-name> kafka-topics.sh --list --bootstrap-server localhost:9092
```

In this case: 

```bash
docker exec -it kafka kafka-topics.sh --list --bootstrap-server localhost:9092
```

This should list the `air-quality` topic among others.

### 4. Install Python Dependencies

Install the required Python dependencies:

```bash
pip install kafka-python requests
```

### 5. Run the Producer

1. **Execute the Producer** to start sending data to Kafka:

```bash
python producer.py
```

The producer will continuously fetch data from the API and send it to the Kafka topic every 60 seconds.

### 6. Run the Consumer

1. **Execute the Consumer** to start listening for messages from Kafka and saving them into a JSON file:

```bash
python consumer_2.py
```

The consumer will listen to the `air-quality` Kafka topic and store the data into `air_quality_data.json`.

### 7. Verifying Producer and Consumer

1. **Producer Output:**

Check the Producer logs to verify that messages are being sent to Kafka. You should see messages like this:

```bash
✅ Sent X records to Kafka
```

2. **Consumer Output:**

Check the Consumer logs to verify that messages are being consumed and written to the JSON file. You should see logs like this:

```bash
✅ Updated air_quality_data.json with X total records
```

You can also open the `air_quality_data.json` file to verify that it contains the data.

### 8. Stopping the Services

Once you're done, stop the Docker containers:

```bash
docker-compose down
```

---

### Conclusion

Now you have a working Kafka setup with a Producer fetching data from an API and a Consumer writing it to a file. You can modify this setup for other use cases or scale it as needed.