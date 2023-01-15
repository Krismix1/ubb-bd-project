#!/usr/bin/env bash

# docker cp project/kafka_consumer.py spark:/
# pip install pandas pyarrow
# export HADOOP_USER_NAME=root or sudo -u hdfs spark-submit
# KAFKA_HOST=kafka:29092
# SP_HOST=spark://spark:7077
# spark-submit --master spark://localhost:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 /kafka_consumer.py
# --master yarn: When running with master 'yarn' either HADOOP_CONF_DIR or YARN_CONF_DIR must be set in the environment
# https://sparkbyexamples.com/spark/spark-submit-command/
HADOOP_USER_NAME=root spark-submit --master spark://localhost:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 project/kafka_hadoop.py

# manager info
# https://stackoverflow.com/questions/66824271/cluster-deploy-mode-is-currently-not-supported-for-python-applications-on-standa
# https://spark.apache.org/docs/latest/cluster-overview.html
# https://spark.apache.org/docs/latest/running-on-yarn.html
