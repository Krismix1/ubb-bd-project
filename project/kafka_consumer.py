# deprecation note:
# https://spark.apache.org/docs/3.3.1/streaming-programming-guide.html

# integration notes
# https://spark.apache.org/docs/3.3.1/structured-streaming-kafka-integration.html

import json
import math
import os
from collections import defaultdict

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    ArrayType,
    BooleanType,
    FloatType,
    IntegerType,
    StructType,
    TimestampType,
)

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
    # dict keys are flight IDs; we probably should focus on aircraft ID later;
    # values are tuples of:
    # 0: aircraft number
    # 1: latitute
    # 2: longitude
    # 3: heading (in degrees)
    # 4: altitude (in feet)
    # 5: speed relative to ground (in kts)
    # 6: some empty string
    # 7:
    # 8: Aircraft model number
    # 9: aircraft Registration number
    # 10: sensor datapoint timestamp?
    # 11: origin airport ID
    # 12: destination airport ID
    # 13: another ID, some identification number
    # 14: number
    # 15: number
    # 16: callsign
    # 17: number
    # 18: airline icao (code?)
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
    # print("----------------------")
    # print(group_key)
    # print("----------------------")
    # print(p_df)
    p_df["lat_diff"] = p_df.latitude.diff()
    p_df["long_diff"] = p_df.longitude.diff()
    p_df["alt_diff"] = p_df.altitude.diff()
    p_df["has_moved"] = (
        (p_df.lat_diff != 0) | (p_df.long_diff != 0) | (p_df.alt_diff != 0)
    )
    return p_df


flight_schema_with_diff = (
    flight_schema.add("lat_diff", FloatType())
    .add("long_diff", FloatType())
    .add("alt_diff", IntegerType())
    .add("timestamp", TimestampType())
    .add("has_moved", BooleanType())
)

# https://insight-trucks.com/en/calculate_fuel_consumption/

liters_per_km_by_engine_type = defaultdict(lambda: 100)


def gcdist(lat1, lon1, lat2, lon2):
    # Great Circle Distance Formula
    # The radius in KM
    R = 6378.137

    # the formula requires we convert all degrees to radians
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)

    lat_span = lat1 - lat2
    lon_span = lon1 - lon2

    a = math.sin(lat_span / 2) ** 2
    b = math.cos(lat1)
    c = math.cos(lat2)
    d = math.sin(lon_span / 2) ** 2

    dist = 2 * R * math.asin(math.sqrt(a + b * c * d))

    return dist


diff_df = groupped_flights_df.applyInPandas(compute_diff, flight_schema_with_diff)

# query2 = diff_df.dropna().filter(diff_df.lat_diff > 0).select("*")
query2 = diff_df.dropna().filter(diff_df.flight_id == "2e61ed80").select("*")
stream_query = query2.writeStream.outputMode("append").format("console").start()
stream_query.awaitTermination(timeout=300)

# (
#     query2.writeStream.format("json")
#     .option("path", "./output")
#     .option("checkpointLocation", "./checkpoints")
#     .start()
#     .awaitTermination(timeout=120)
# )
