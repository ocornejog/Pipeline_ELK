# Air Quality Index Processing Guide

This document outlines the necessary steps to inject our data to elastic search, so we have to validate that both of us have the same number of documents and with the same distribution by day.

## Steps

### 1. Delete the Existing Index in Elasticsearch
To remove the current `air_quality` index, execute the following command:
```sh
curl -X DELETE "http://localhost:9200/air_quality"
```

### 2. Verify Index Deletion
To ensure that the index has been successfully deleted, run:
```sh
curl -X GET "http://localhost:9200/_cat/indices?pretty"
```
If the index no longer appears in the output, it has been successfully removed.

### 3. Run the Producer Script
Execute `producer.py` to process and send data to Elasticsearch:
```sh
python producer.py
```
> **Note:** During execution, some csv files may not be processed if they no longer exist (check the logs). If `producer.py` continues running, it will attempt to access these files again after completion.

### 4. Verify Index Creation in Elasticsearch
After running `producer.py`, confirm that the `air_quality` index has been created:
```sh
curl -X GET "http://localhost:9200/_cat/indices?pretty"
```

### 5. Count the Number of Documents
To check the number of documents in the index:
```sh
curl -X GET "http://localhost:9200/air_quality/_count?pretty"
```

### 6. Analyze Date Distribution
To inspect the distribution of documents by date, execute the following aggregation query:
```sh
curl -X GET "http://localhost:9200/air_quality/_search?pretty" -H "Content-Type: application/json" -d '
{
  "size": 0,
  "aggs": {
    "unique_dates": {
      "date_histogram": {
        "field": "Date de debut",
        "calendar_interval": "day",
        "format": "yyyy/MM/dd"
      }
    }
  }
}'
```

