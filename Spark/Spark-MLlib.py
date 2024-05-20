from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF, StringIndexer
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

spark = SparkSession.builder \
    .appName("SentimentAnalysis") \
    .master("local[*]") \
    .getOrCreate()

schema = StructType([
    StructField("TweetID", IntegerType(), True),
    StructField("Entity", StringType(), True),
    StructField("Sentiment", StringType(), True),
    StructField("Content", StringType(), True)
])

df = spark.read.csv("twitter_training.csv", header=False, schema=schema)

df = df.filter(df["Content"].isNotNull())

tokenizer = Tokenizer(inputCol="Content", outputCol="words")
df_words = tokenizer.transform(df)

remover = StopWordsRemover(inputCol="words", outputCol="filtered")
df_filtered = remover.transform(df_words)

hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures")
featurizedData = hashingTF.transform(df_filtered)
idf = IDF(inputCol="rawFeatures", outputCol="features")
idfModel = idf.fit(featurizedData)
rescaledData = idfModel.transform(featurizedData)

idfModel.save("IDF_V1")  

indexer = StringIndexer(inputCol="Sentiment", outputCol="label")
indexer_model = indexer.fit(rescaledData)
df_final = indexer_model.transform(rescaledData)

train_data, test_data = df_final.randomSplit([0.8, 0.2], seed=1234)

lr = LogisticRegression(featuresCol='features', labelCol='label')
lrModel = lr.fit(train_data)
predictions = lrModel.transform(test_data)

evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Logistic Regression Accuracy: %f" % accuracy)

with open("sentiment_to_index_mapping.txt", "w") as file:
    labels_to_index = indexer_model.labels
    for index, label in enumerate(labels_to_index):
        file.write(f"Numeric index {index} corresponds to Sentiment: '{label}'\n")

lrModel.save("V1")

predictions.select("Content", "label", "prediction").show()

spark.stop()
