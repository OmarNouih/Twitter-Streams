from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF, StringIndexer
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql.functions import rand

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

# Take 50% of the data and shuffle it
df_sampled = df.sample(False, 0.5).orderBy(rand())

# Tokenization
tokenizer = Tokenizer(inputCol="Content", outputCol="words")
df_words = tokenizer.transform(df_sampled)

# Remove stopwords
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
df_filtered = remover.transform(df_words)

# TF-IDF
hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures")
featurizedData = hashingTF.transform(df_filtered)
idf = IDF(inputCol="rawFeatures", outputCol="features")
idfModel = idf.fit(featurizedData)
rescaledData = idfModel.transform(featurizedData)

# Index 'Sentiment' column
indexer = StringIndexer(inputCol="Sentiment", outputCol="label")
indexer_model = indexer.fit(rescaledData)
df_final = indexer_model.transform(rescaledData)

# Define Decision Tree Classifier model
dt = DecisionTreeClassifier(featuresCol='features', labelCol='label')

# Fit the model
dtModel = dt.fit(df_final)

# Evaluate the model
predictions = dtModel.transform(df_final)
evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Decision Tree Classifier Accuracy: %f" % accuracy)

# Save accuracy to file
with open("DT_accuracy.txt", "w") as file:
    file.write("Decision Tree Classifier Accuracy: %f\n" % accuracy)

# Save the model
dtModel.save("DT_model")

# Display predictions
predictions.select("Content", "label", "prediction").show()

# Stop SparkSession
spark.stop()
