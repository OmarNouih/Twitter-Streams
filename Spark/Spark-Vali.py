from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF
from pyspark.ml.classification import LogisticRegressionModel
from pyspark.sql.functions import udf
from pyspark.sql.types import FloatType
from pymongo import MongoClient
from pyspark.ml.feature import IDFModel

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("RealTimePrediction") \
    .master("local[*]") \
    .getOrCreate()

# Define schema for DataFrame
schema = StructType([
    StructField("TweetID", IntegerType(), True),
    StructField("Entity", StringType(), True),
    StructField("Sentiment", StringType(), True),
    StructField("Content", StringType(), True)
])

# Load the saved model
model = LogisticRegressionModel.load("V1")

# Load the IDF model
idfModel = IDFModel.load("IDF_V1")  # Specify the correct path where the IDF model is saved

# Read CSV file into DataFrame for real-time validation data
df_validation = spark.read.csv("twitter_validation.csv", header=False, schema=schema)

# Apply preprocessing steps
df_validation_filtered = df_validation.filter(df_validation["Content"].isNotNull())
df_validation_filtered = df_validation_filtered.fillna({"Content": "default_value"})

# Tokenization
tokenizer = Tokenizer(inputCol="Content", outputCol="words")
df_validation_words = tokenizer.transform(df_validation_filtered)

# Remove stopwords
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
df_validation_filtered = remover.transform(df_validation_words)

# TF-IDF (using the loaded IDF model)
hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures")
featurized_validation_data = hashingTF.transform(df_validation_filtered)
rescaled_validation_data = idfModel.transform(featurized_validation_data)

# Make real-time predictions
predictions = model.transform(rescaled_validation_data)

# Extract maximum probability as confidence
get_max_prob = udf(lambda v: float(max(v)), FloatType())
predictions = predictions.withColumn("confidence", get_max_prob("probability"))

# Select relevant columns to save: Tweet content, prediction and confidence
predictions_to_save = predictions.select("Content", "prediction", "confidence")

# Convert to Pandas DataFrame
predictions_pandas = predictions_to_save.toPandas()

# Initialize PyMongo client
client = MongoClient("mongodb://host.docker.internal:27017")
# Select the database and collection
db = client["BigData"]
collection = db["Validation"]

# Insert predictions into MongoDB collection
collection.insert_many(predictions_pandas.to_dict(orient='records'))

# Stop SparkSession
spark.stop()
