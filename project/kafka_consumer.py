# deprecation note:
# https://spark.apache.org/docs/3.3.1/streaming-programming-guide.html

# integration notes
# https://spark.apache.org/docs/3.3.1/structured-streaming-kafka-integration.html

import json
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, MapType, StringType, StructType

os.environ[
    "PYSPARK_SUBMIT_ARGS"
] = "--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 pyspark-shell"


flight_schema = (
    StructType()
    .add("flight_id", "string", False)
    .add("aircraft_number", "string", False)
    .add("latitude", "float", False)
    .add("longitude", "float", False)
    .add("altitude", "integer", False)
)
kafka_message_schema = ArrayType(flight_schema)


@F.udf(kafka_message_schema)
def custom_json_converter(json_string: str):
    data = json.loads(json_string)
    return [
        {
            "flight_id": key,
            "aircraft_number": values[0],
            "latitude": values[1],
            "longitude": values[2],
            "altitude": values[3],
        }
        for key, values in data.items()
        if key not in ("version", "full_count")
    ]


spark = SparkSession.builder.getOrCreate()

df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "flights_raw")
    .option("startingOffsets", "earliest")
    .load()
)

transformed_df = df.selectExpr("CAST(value AS STRING) as json_entry").select(
    F.explode(custom_json_converter("json_entry")).alias("flight_data"),
)
query2 = transformed_df.select("flight_data.*")
stream_query = query2.writeStream.outputMode("append").format("console").start()
stream_query.awaitTermination(timeout=10)
