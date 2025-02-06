# Data transmission with Kafka 
## Kafka Producer and Consumer Setup

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


# Data Transformation and Indexing (Logstash)

## 1️⃣ Stop Logstash and Remove Old Configurations

Stop Logstash:

```bash
sudo systemctl stop logstash
```

Remove all `.conf` configurations inside Logstash:

```bash
sudo rm -rf /etc/logstash/conf.d/*
```

## 2️⃣ Create a New Configuration File

Open a new configuration file:

```bash
sudo nano /etc/logstash/conf.d/logstash_kafka.conf
```

Copy and paste this content:

```plaintext
input {
  kafka {
    bootstrap_servers => "localhost:9092"
    topics => ["air-quality"]
    codec => "json"
  }
}

filter {
  mutate {
    convert => {
      "10nata" => "float"
      "25nata" => "float"
      "tnata" => "float"
      "hynata" => "float"
    }
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "air_quality"
    document_id => "%{dateheure}"  # Overwrites data if the same dateheure exists
  }
  stdout { codec => rubydebug }
}
```

Save and close (CTRL + X, then Y and ENTER).

## 3️⃣ Verify the File Syntax

Before restarting Logstash, check if the `.conf` file has errors:

```bash
sudo /usr/share/logstash/bin/logstash --config.test_and_exit --path.settings /etc/logstash
```

If there are no errors, you will see a message like:

```plaintext
Configuration OK
```

If there are errors, check the problematic lines and fix them.

## 4️⃣ Restart Logstash

If the configuration is valid, start Logstash again:

```bash
sudo systemctl start logstash
```

Enable Logstash to start automatically with the system:

```bash
sudo systemctl enable logstash
```

## 5️⃣ Check That Logstash Is Running

Check its status:

```bash
sudo systemctl status logstash
```

If everything is fine, you will see something like:

```plaintext
Active: active (running)
```

You can also view real-time logs to verify that it is processing data:

```bash
sudo journalctl -u logstash -f
```

## 6️⃣ Verify That Data Reaches Elasticsearch

After waiting a few minutes, check if `air_quality` appears in Elasticsearch:

```bash
curl -X GET "http://localhost:9200/_cat/indices?v"
```

If you see `air_quality`, it means Logstash is sending data.
To view some records:

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty"
```

# Elastic Search queries with mapping

## Exercise 1: Text Query

### Mapping
The mapping for the text query does not require special changes, but ensure that fields are correctly defined.

```bash
curl -X PUT "http://localhost:9200/air_quality?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "dateheure": {
        "type": "date"
      },
      "10nata": {
        "type": "float"
      },
      "25nata": {
        "type": "float"
      },
      "tnata": {
        "type": "float"
      },
      "hynata": {
        "type": "float"
      }
    }
  }
}
'
```

### Query
**Description:** Search for documents where the field "25nata" exactly matches the value 54.

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "25nata": "54"
    }
  }
}
'
```

## Exercise 2: Aggregation Query

### Mapping
The mapping for the aggregation query remains the same as the previous one.

```bash
curl -X PUT "http://localhost:9200/air_quality?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "dateheure": {
        "type": "date"
      },
      "10nata": {
        "type": "float"
      },
      "25nata": {
        "type": "float"
      },
      "tnata": {
        "type": "float"
      },
      "hynata": {
        "type": "float"
      }
    }
  }
}
'
```

### Query
**Description:** Calculate the average value of the "hynata" field for all documents.

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "avg_hynata": {
      "avg": {
        "field": "hynata"
      }
    }
  }
}
'
```

## Exercise 3: N-gram Query

### Mapping
For the N-gram query, we convert the "10nata" field to text type and define a custom analyzer.

```bash
curl -X PUT "http://localhost:9200/air_quality?pretty" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "analysis": {
      "analyzer": {
        "my_ngram_analyzer": {
          "tokenizer": "my_ngram_tokenizer"
        }
      },
      "tokenizer": {
        "my_ngram_tokenizer": {
          "type": "ngram",
          "min_gram": 2,
          "max_gram": 3,
          "token_chars": [
            "letter",
            "digit"
          ]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "dateheure": {
        "type": "date"
      },
      "10nata": {
        "type": "text",
        "analyzer": "my_ngram_analyzer"
      },
      "25nata": {
        "type": "float"
      },
      "tnata": {
        "type": "float"
      },
      "hynata": {
        "type": "float"
      }
    }
  }
}
'
```

### Query
**Description:** Search for documents where the "10nata" field (converted to text) contains N-grams that match "68".

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "10nata": "68"
    }
  }
}
'
```

## Exercise 4: Fuzzy Query

### Mapping
For the fuzzy query, we convert the "10nata" field to text type.

```bash
curl -X PUT "http://localhost:9200/air_quality?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "dateheure": {
        "type": "date"
      },
      "10nata": {
        "type": "text"
      },
      "25nata": {
        "type": "float"
      },
      "tnata": {
        "type": "float"
      },
      "hynata": {
        "type": "float"
      }
    }
  }
}
'
```

### Query
**Description:** Search for documents where the "10nata" field (converted to text) has values similar to "69", allowing a margin of error (fuzziness).

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "fuzzy": {
      "10nata": {
        "value": "6,=",
        "fuzziness": 2
      }
    }
  }
}
'
```

## Exercise 5: Time Series Query

### Mapping
The mapping for the time series query remains the same as the initial mapping.

```bash
curl -X PUT "http://localhost:9200/air_quality?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "dateheure": {
        "type": "date"
      },
      "10nata": {
        "type": "float"
      },
      "25nata": {
        "type": "float"
      },
      "tnata": {
        "type": "float"
      },
      "hynata": {
        "type": "float"
      }
    }
  }
}
'
```

### Query
**Description:** Retrieve the average "tnata" field value grouped by hour ("dateheure").

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "tnata_over_time": {
      "date_histogram": {
        "field": "dateheure",
        "calendar_interval": "year"
      },
      "aggs": {
        "avg_tnata": {
          "avg": {
            "field": "tnata"
          }
        }
      }
    }
  }
}
'
```

## Final Notes

- **Deleting and recreating the index:** If the `air_quality` index already exists, delete it before applying a new mapping:

  ```bash
  curl -X DELETE "http://localhost:9200/air_quality?pretty"
  ```

- **Reindexing:** If you need to reindex data from an existing index, use Elasticsearch's `_reindex` command.
