# Documentation: Pipeline ELK sur les taux de pollution 

# 1. Kafka Producer and Consumer Setup

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
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
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


# 2. Create Index Template in Elasticsearch

## 1️. Create the Template JSON File

Create the template file:

```bash
sudo nano /etc/logstash/templates/template.json
```

Copy and paste this content:

```json
{
  "index_patterns": ["air_quality*"],
  "settings": {
    "analysis": {
      "analyzer": {
        "ngram_analyzer": {
          "type": "custom",
          "tokenizer": "ngram_tokenizer",
          "filter": ["lowercase"]
        }
      },
      "tokenizer": {
        "ngram_tokenizer": {
          "type": "ngram",
          "min_gram": 3,
          "max_gram": 4,
          "token_chars": ["letter", "digit"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "@timestamp": {
        "type": "date"
      },
      "Date de debut": {
        "type": "date",
        "format": "yyyy/MM/dd HH:mm:ss||yyyy/MM/dd||epoch_millis||strict_date_optional_time"
      },
      "Date de fin": {
        "type": "date",
        "format": "yyyy/MM/dd HH:mm:ss||yyyy/MM/dd||epoch_millis||strict_date_optional_time"
      },
      "Organisme": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          },
          "ngram": {
            "type": "text",
            "analyzer": "ngram_analyzer"
          }
        }
      },
      "Polluant": {
        "type": "keyword"
      },
      "Reglementaire": {
        "type": "keyword"
      },
      "Zas": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "code qualite": {
        "type": "keyword"
      },
      "code site": {
        "type": "keyword"
      },
      "code zas": {
        "type": "keyword"
      },
      "couverture de donnees": {
        "type": "float"
      },
      "couverture temporelle": {
        "type": "float"
      },
      "discriminant": {
        "type": "keyword"
      },
      "nom site": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          },
          "ngram": {
            "type": "text",
            "analyzer": "ngram_analyzer"
          }
        }
      },
      "procedure de mesure": {
        "type": "keyword"
      },
      "taux de saisie": {
        "type": "float"
      },
      "type d'evaluation": {
        "type": "keyword"
      },
      "type d'implantation": {
        "type": "keyword"
      },
      "type d'influence": {
        "type": "keyword"
      },
      "type de valeur": {
        "type": "keyword"
      },
      "unite de mesure": {
        "type": "keyword"
      },
      "valeur": {
        "type": "float"
      },
      "valeur brute": {
        "type": "float"
      },
      "validite": {
        "type": "integer"
      },
      "quality_level": {
        "type": "keyword"
      }
    }
  }
}
```

## 2️. Create the Index Template in Elasticsearch

Run the following command to create the index template in Elasticsearch:

```bash
curl -X PUT "http://localhost:9200/_template/air_quality_template" -H 'Content-Type: application/json' -d @/etc/logstash/templates/template.json
```

## 3. Verify the Index Template
Check if the template was created successfully:

```bash
curl -X GET "http://localhost:9200/_template/air_quality_template?pretty"
```

# 3. Data Transformation and Indexing (Logstash)

## 1️. Stop Logstash and Remove Old Configurations

Stop Logstash:

```bash
sudo systemctl stop logstash
```

Remove all `.conf` configurations inside Logstash:

```bash
sudo rm -rf /etc/logstash/conf.d/*
```

## 2️. Create a New Configuration File

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
    client_id => "logstash_air_quality"
    group_id => "logstash_air_quality_group"
    auto_offset_reset => "latest"
    consumer_threads => 3
  }
}

filter {
  date {
    match => ["Date de debut",
    "yyyy/MM/dd HH:mm:ss"]
    target => "timestamp_debut"
  }
  date {
    match => ["Date de fin",
    "yyyy/MM/dd HH:mm:ss"]
    target => "timestamp_fin"
  }
  mutate {
    convert => {
      "valeur" => "float"
      "valeur brute" => "float"
      "taux de saisie" => "float"
      "couverture temporelle" => "float"
      "couverture de donnees" => "float"
      "validite" => "integer"
    }
  }
  mutate {
    remove_field => ["event", "filename"]
  }
  if [code qualite] == "A" {
    mutate {
      add_field => { "quality_level" => "high" }
    }
  } else if [code qualite] == "R" {
    mutate {
      add_field => { "quality_level" => "medium" }
    }
  } else {
    mutate {
      add_field => { "quality_level" => "low" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "air_quality"
    document_id => "%{@timestamp}"
  }
  stdout { codec => rubydebug }
}
```

Save and close (CTRL + X, then Y and ENTER).

## 3️. Verify the File Syntax

Before restarting Logstash, check if the `.conf` file has errors:

```bash
sudo /usr/share/logstash/bin/logstash --config.test_and_exit --path.settings /etc/logstash
```

If there are no errors, you will see a message like:

```plaintext
Configuration OK
```

If there are errors, check the problematic lines and fix them.

## 4️. Restart Logstash

If the configuration is valid, start Logstash again:

```bash
sudo systemctl start logstash
```

Enable Logstash to start automatically with the system:

```bash
sudo systemctl enable logstash
```

## 5️. Check That Logstash Is Running

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

## 6️. Verify That Data Reaches Elasticsearch

After waiting a few minutes, check if `air_quality` appears in Elasticsearch:

```bash
curl -X GET "http://localhost:9200/_cat/indices?v"
```

If you see `air_quality`, it means Logstash is sending data.
To view some records:

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty"
```

# 4. Elasticsearch Queries with Mapping

## Query 1: Text query

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "Organisme": "Atmo"
    }
  }
}'
```

## Query 2: Query including an aggregation

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "quality_counts": {
      "terms": {
        "field": "quality_level",
        "size": 3
      }
    }
  }
}'
```

And also:

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "pollutant_distribution": {
      "terms": {
        "field": "Polluant",
        "size": 10
      },
      "aggs": {
        "percentage": {
          "bucket_script": {
            "buckets_path": {
              "count": "_count"
            },
            "script": "params.count * 100 / 307403"
          }
        }
      }
    }
  }
}'
```
## Query 3: N-gram query

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "nom site.ngram": "SAI"
    }
  }
}'
```

## Query 4: Fuzzy queries

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "fuzzy": {
      "nom site": {
        "value": "Arbes",
        "fuzziness": 2
      }
    }
  }
}'
```

Pour vérifier:

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty" -H "Content-Type: application/json" -d '{
  "size": 0,
  "query": {
    "fuzzy": {
      "nom site": {
        "value": "Arbes",
        "fuzziness": 2
      }
    }
  },
  "aggs": {
    "unique_nom_site": {
      "terms": {
        "field": "nom site.keyword",
        "size": 1000,
        "order": { "_key": "asc" }
      }
    }
  }
}'
```

## Query 5: Time series

```bash
curl -X GET "http://localhost:9200/air_quality/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        {
          "term": {
            "nom site.keyword": "Concorde"
          }
        },
        {
          "term": {
            "Polluant": "NO"
          }
        },
        {
          "range": {
            "Date de debut": {
              "gte": "2025-02-01T00:00:00",
              "lt": "2025-02-20T00:00:00"
            }
          }
        }
      ]
    }
  },
  "aggs": {
    "daily_values": {
      "date_histogram": {
        "field": "Date de debut",
        "calendar_interval": "day"
      },
      "aggs": {
        "average_valeur": {
          "avg": {
            "field": "valeur"
          }
        }
      }
    }
  }
}'
```

# 5. Data processing with Spark

# 1 Sending data to Spark

Execute the following code initializes a Spark session, configures the settings to connect to Elasticsearch, and loads the data into a DataFrame: 

```java
import org.apache.spark.sql.SparkSession

// Importation des implicites pour utiliser les fonctionnalités Spark SQL
import spark.implicits._

// Arrêt d'une session active si elle existe
SparkSession.getActiveSession.foreach(_.stop())

// Création d'une nouvelle session Spark avec connexion à Elasticsearch
val spark = SparkSession.builder()
    .appName("Read from ES")
    .config("spark.es.nodes", "localhost")
    .config("spark.es.port", "9200")
    .config("spark.es.mapping.date.rich", "false")
    .config("spark.es.nodes.wan.only", "true")
    .master("local[*]")
    .getOrCreate()

// Chargement des données d'Elasticsearch dans un DataFrame Spark
val air_quality_polDF = spark.read
    .format("org.elasticsearch.spark.sql")
    .option("es.read.fields.as.array.include", "")
    .option("es.mapping.date.rich", "false")
    .load("air_quality")

// Affichage du schéma des données chargées
air_quality_polDF.printSchema()
```
# 2. Analysis by Location Type

```java
val avgByImplantation = air_quality_polDF
.groupBy("type d'implantation")
.agg(
avg("valeur").as("moyenne_pollution"),
count("*").as("nombre_mesures")
)
.orderBy(desc("moyenne_pollution"))
```

# 3. Performance of Organizations

```java
val avgPollutionByZAS = air_quality_polDF
  .groupBy("Zas")
  .agg(
    avg("valeur").as("moyenne_pollution")
  )
  .orderBy(desc("moyenne_pollution"))
```

# 4. Data quality

```java
val qualityDistribution = air_quality_polDF
.groupBy("quality_level")
.count()
.orderBy(desc("count"))
```

# 5. Extreme values

```java
val mostCommonPollutants = air_quality_polDF
  .groupBy("Polluant")
  .agg(
    count("*").as("nombre_mesures")
  )
  .orderBy(desc("nombre_mesures"))
```

# 6. Global Statistics

```java
val globalStats = air_quality_polDF.agg(
avg("valeur").as("moyenne_globale"),
stddev("valeur").as("ecart_type"),
min("valeur").as("min"),
max("valeur").as("max"),
count("*").as("total_mesures")
)
```

## Final Notes

- **Deleting and recreating the index:** If the `air_quality` index already exists, delete it before applying a new mapping:

  ```bash
  curl -X DELETE "http://localhost:9200/air_quality?pretty"
  ```

- **Reindexing:** If you need to reindex data from an existing index, use Elasticsearch's `_reindex` command.
