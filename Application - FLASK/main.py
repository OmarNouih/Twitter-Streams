import os
import re
import time
from flask import Flask, jsonify, render_template, request, redirect, stream_with_context, Response
from kafka import KafkaProducer
import json
import pandas as pd
from pymongo import MongoClient
from bson.json_util import dumps

os.environ['PYTHONIOENCODING'] = 'utf-8'

app = Flask(__name__)
app.secret_key = 'TESTING' 

producer = KafkaProducer(bootstrap_servers = ['localhost:9092'], value_serializer=  lambda x: json.dumps(x).encode('utf-8'))
uri = "UR MONGODB CLUSTER"

def watch_changes():
    client = MongoClient(uri)
    db = client["BigData"]
    collection = db["TweetsPredictions"]
    change_stream = collection.watch([{'$match': {'operationType': 'insert'}}])
    for change in change_stream:
        yield 'data: {}\n\n'.format(dumps(change['fullDocument']))

def map_prediction_to_sentiment(prediction):
    sentiments = {
        0: 'Negative',
        1: 'Positive',
        2: 'Neutral',
        3: 'Irrelevant'
    }
    return sentiments.get(prediction, 'Unknown')

@app.route('/stream_inserts')
def stream_inserts():
    def generate():
        for change in watch_changes():
            data = json.loads(change.strip("data:"))
            data["prediction"] = map_prediction_to_sentiment(data["prediction"])
            yield 'data: {}\n\n'.format(json.dumps(data))
    return Response(generate(), mimetype='text/event-stream')

@app.route("/", methods = ['GET'])
def index():
    return render_template('index.html')

@app.route("/stream", methods=['GET'])
def test():
    return render_template('streaming.html')

@app.route("/validation", methods=['GET'])
def validation():
    client = MongoClient("mongodb://localhost:27017")
    db = client["BigData"]
    collection = db["Validation"]
    predictions = list(collection.find({}, {"_id": 0, "TweetID": 1, "Content": 1, "prediction": 1, "confidence": 1}))
    return render_template('validation.html', predictions=predictions)

@app.route('/produce_tweets', methods = ['POST'])
def clear_tweets():
    data = request.json
    tweet_content = data['tweetContent']
    pattern = re.compile(r'[^\w\s.,!?;:\-\'"&()]')
    tweet_content = pattern.sub('', tweet_content)
    print("Received tweet content:", tweet_content)
    producer.send('tweets', value = tweet_content)
    return jsonify({"tweetContent": tweet_content})

@app.route('/stream_csv', methods=['GET'])
def stream_csv():
    def generate():
        data = pd.read_csv('./Spark/twitter_validation.csv', encoding='utf-8')
        for index, row in data.iterrows():
            json_data = json.dumps({"content": row[3]})
            yield f"{json_data}\n"
            time.sleep(5)  
            
    return Response(stream_with_context(generate()), mimetype='application/json')

if __name__ == "__main__":
    app.run()