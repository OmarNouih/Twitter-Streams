# Real-Time Sentiment Analysis on Twitter Streams

## Project Creators
- NOUIH Omar
- AIT AHMED Aymen
- BEZZAR Nouhaila

## Overview
This project develops a web application for real-time sentiment analysis of Twitter streams using Apache Kafka and machine learning models. The application categorizes each tweet as Negative, Positive, Neutral, or Irrelevant.

## Multimedia Content
- **Video Demonstration**

https://github.com/OmarNouih/Twitter-Streams/assets/27814897/04f5149b-f44d-4218-b10e-1583bfb92ee7

## Architecture
- **APP**: Flask application, static resources, and HTML templates.
- **Spark**: Machine learning and stream processing scripts, datasets.

## Setup Instructions

### Docker Setup for Kafka
To get Kafka running via Docker, execute the following commands:
```bash
cd path_to_project_directory
docker-compose up -d
```

### Building the Spark-Jupyter Docker Image
Build the Docker image using the Dockerfile provided:
```bash
docker build -t spark-jupyter:latest .
```

### Docker Container for Spark
Run the Docker container, ensuring to mount the Spark directory so that it is accessible within the container:
```bash
docker run -p 8888:8888 -v path_to_your_project_directory/Spark:/home/jovyan/work spark-jupyter:latest
```
This mounts the `Spark` directory to `/home/jovyan/work` within the Jupyter environment.

### Training the Sentiment Analysis Model
Navigate to the Spark directory and execute the training script:
```bash
spark-submit Spark-MLlib.py
```

### Streaming with Kafka
Start the Kafka streaming process with the following command:
```bash
spark-submit Kafka-Streaming.py
```

### MongoDB Setup
Ensure MongoDB is operational and the URI is set up as per your `main.py` , `Kafka-Streaming.py` configuration.

## Flask Application Usage
- `/stream_inserts`: Endpoint for real-time stream inserts.
- `/`: Homepage and stream testing.
- `/stream`: Stream simulation interface.
- `/validation`: Model validation and predictions display.
- `/produce_tweets`: Processes and queues tweets for analysis.
- `/stream_csv`: Streams validation data for real-time analysis.

## Data Description
The training dataset `twitter_training.csv` includes tweets with their sentiment labels. The `twitter_validation.csv` dataset contains tweets used for real-time sentiment prediction.

## Tools and Frameworks
The project utilizes Apache Kafka Stream, Spark MLlib, NLTK, Pandas, Matplotlib, Flask, and Django. It is developed in Python with supplementary use of Java and JavaScript.

## Data Source
Twitter Entity Sentiment Analysis data obtained from [Kaggle](https://www.kaggle.com/datasets/jp797498e/twitter-entity-sentiment-analysis).

## Testing Streams
There are two ways to test the streams within the application:
1. Real-time text entry for immediate sentiment analysis.
2. Use the "Start Streaming Tweets" button to initiate streaming from `twitter_validation.csv`. 

## Project Repository
The source code is available at _[[GitHub repository link](https://github.com/OmarNouih/Twitter-Streams/)]_.
