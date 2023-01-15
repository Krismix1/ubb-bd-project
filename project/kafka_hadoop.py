import json
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StructType

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
def custom_json_converter(json_string):
    data = json.loads(json_string)
    return [
        {
            "flight_id": key,
            "aircraft_number": values[0],
            "latitude": values[1],
            "longitude": values[2],
            "altitude": values[4],
        }
        for key, values in data.items()
        if key not in ("version", "full_count")
    ]


flight_schema = (
    StructType()
    .add("flight_id", "string", False)
    .add("aircraft_number", "string", False)
    .add("latitude", "float", False)
    .add("longitude", "float", False)
    .add("altitude", "integer", False)
)
kafka_message_schema = ArrayType(flight_schema)


sp_host = os.environ.get("SP_HOST", "spark://localhost:7077")
spark = SparkSession.builder.master(sp_host).getOrCreate()

df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", os.environ.get("KAFKA_HOST", "localhost:9092"))
    .option("subscribe", "flights_raw")
    .option("startingOffsets", "earliest")
    .option("failOnDataLoss", "false")
    .option("groupIdPrefix", "spark_kafka_hadoop")
    # .option("kafka.group.id", "kafka_hadoop")
    .load()
)

flights_df = df.select(
    df.timestamp,
    F.explode(custom_json_converter(df.value.cast("string"))).alias("flight_data"),
)


stream_query = (
    flights_df.writeStream.format("parquet")
    .option("checkpointLocation", "hdfs://localhost/checkpoints")
    .option("path", "hdfs://localhost/testme")
    .start()
)
stream_query.awaitTermination(timeout=300)
