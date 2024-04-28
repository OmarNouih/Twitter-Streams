from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF, StringIndexer
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("SentimentAnalysis") \
    .master("local[*]") \
    .getOrCreate()

# Define schema for DataFrame
schema = StructType([
    StructField("TweetID", IntegerType(), True),
    StructField("Entity", StringType(), True),
    StructField("Sentiment", StringType(), True),
    StructField("Content", StringType(), True)
])

# Read CSV file into DataFrame
df = spark.read.csv("twitter_training.csv", header=False, schema=schema)

# Remove null values from 'Content' column
df = df.filter(df["Content"].isNotNull())

# Tokenization
tokenizer = Tokenizer(inputCol="Content", outputCol="words")
df_words = tokenizer.transform(df)

# Remove stopwords
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
df_filtered = remover.transform(df_words)

# TF-IDF
hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures")
featurizedData = hashingTF.transform(df_filtered)
idf = IDF(inputCol="rawFeatures", outputCol="features")
idfModel = idf.fit(featurizedData)
rescaledData = idfModel.transform(featurizedData)

# Save the IDF Model
idfModel.save("IDF_V1")  # Specify a path to save the IDF model

# Index 'Sentiment' column
indexer = StringIndexer(inputCol="Sentiment", outputCol="label")
indexer_model = indexer.fit(rescaledData)
df_final = indexer_model.transform(rescaledData)

# Logistic Regression model
lr = LogisticRegression(featuresCol='features', labelCol='label')
lrModel = lr.fit(df_final)
predictions = lrModel.transform(df_final)

# Evaluate the model
evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Logistic Regression Accuracy: %f" % accuracy)

# Save the sentiment to index mapping to a text file
with open("sentiment_to_index_mapping.txt", "w") as file:
    labels_to_index = indexer_model.labels
    for index, label in enumerate(labels_to_index):
        file.write(f"Numeric index {index} corresponds to Sentiment: '{label}'\n")

# Save the model
lrModel.save("V1")

# Display predictions
predictions.select("Content", "label", "prediction").show()

# Stop SparkSession
spark.stop()
