# deprecation note:
# https://spark.apache.org/docs/3.3.1/streaming-programming-guide.html

# integration notes
# https://spark.apache.org/docs/3.3.1/structured-streaming-kafka-integration.html

import json
import os

import pandas as pd
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

flights_df = df.select(
    df.timestamp,
    F.explode(custom_json_converter(df.value.cast("string"))).alias("flight_data"),
)

# https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#window-operations-on-event-time
# drop data if it's older than 1 hour
groupped_flights_df = (
    flights_df.select("timestamp", "flight_data.*")
    .withWatermark("timestamp", "1 hour")
    .groupBy(F.window("timestamp", "30 seconds"), "flight_id")
)


def compute_diff(group_key: tuple[dict, str], p_df: pd.DataFrame):
    return pd.DataFrame(
        {
            "start": group_key[0]["start"],
            "end": group_key[0]["end"],
            "flight_id": group_key[1],
            "lat_diff": p_df.latitude.diff(),
            "long_diff": p_df.longitude.diff(),
            "alt_diff": p_df.altitude.diff(),
        }
    )


diff_df = groupped_flights_df.applyInPandas(
    compute_diff,
    schema="start timestamp, end timestamp, flight_id string, lat_diff float, long_diff float, alt_diff integer",
)

query2 = diff_df.dropna().filter(diff_df.lat_diff > 0).select("*")
stream_query = query2.writeStream.outputMode("append").format("console").start()
stream_query.awaitTermination(timeout=300)

