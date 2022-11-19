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

# customSchema = StructType().add("full_count", "integer").add("version", "integer")
customSchema = StructType().add("0", "string").add("1", "float")
customSchemaOuter = MapType(StringType(), customSchema)
spark = SparkSession.builder.getOrCreate()

df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    # .option("kafka.bootstrap.servers", "zookeper:2181")
    # .option("subscribe", "topic1")
    .option("subscribe", "flights_raw")
    .option("startingOffsets", "earliest")
    # .schema(customSchema)
    .load()
)

# transformed_df = df.selectExpr("CAST(value AS STRING) as jsonEntry").select(
#     from_json("jsonEntry", customSchema).alias("new_name")
# )
row_type = (
    StructType()
    .add("flight_id", "string", False)
    .add("aircraft_number", "string", False)
    .add("latitude", "float", False)
    .add("longitude", "float", False)
    .add("altitude", "integer", False)
)
another_schema = ArrayType(row_type)


@F.udf(another_schema)
def f_json(json_string: str):
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


transformed_df = (
    df.selectExpr("CAST(value AS STRING) as jsonEntry")
    .select(
        # F.from_json("jsonEntry", "MAP<STRING,STRING>").alias("new_name")
        # F.from_json("new_name", F.schema_of_json("new_name")).alias("new_name")
        # (F.schema_of_json("new_name")).alias("new_name")
        # df.value.cast(StringType()).cast(StructType()).alias("json_string")
        # F.from_json("jsonEntry", customSchemaOuter).alias("new_name")
        f_json("jsonEntry").alias("new_name"),
    )
    .select(F.explode("new_name").alias("new_name"))
)
transformed_df.printSchema()
# df.printSchema()
# df.rdd.map(lambda row: (row, list(json.loads(row).keys()))).collect()

# writer = (
#     transformed_df.select("new_name").writeStream.format("console")
#     # .writeStream.format("memory")
#     .queryName("test_query")
# )
# query = writer.start(queryName="test_query", outputMode="append", format="console")
# query.awaitTermination(timeout=10)
# print(query.status)

# query2 = transformed_df.select("new_name.full_count")
query2 = transformed_df.select("new_name.*")
# query2 = transformed_df.select("new_name")
stream_query = query2.writeStream.outputMode("append").format("console").start()
stream_query.awaitTermination(timeout=10)


# df.select("device").where("signal > 10").groupBy("deviceType").count()
