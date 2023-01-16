# https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DML#LanguageManualDML-Loadingfilesintotables
# https://bigdataprogrammers.com/load-csv-file-in-hive/
# create table if not exists aircrafts(latitude double, altitude float) partitioned by(flight_id string);
# LOAD DATA INPATH '/aircraft_data_processed/part-00000' OVERWRITE INTO TABLE aircrafts;

DDL_QUERY="CREATE SCHEMA IF NOT EXISTS bdp; CREATE EXTERNAL TABLE IF NOT EXISTS bdp.aircrafts_csv_table (latitude double, altitude float, flight_id string) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION 'hdfs://namenode:8020/aircrafts_csv_table';"
DML_QUERY="LOAD DATA INPATH '/aircraft_data_processed/part-00000' OVERWRITE INTO TABLE bdp.aircrafts_csv_table;"

docker exec -it hiveserver /opt/hive/bin/beeline -u 'jdbc:hive2://root@hiveserver:10000/' -e "$DDL_QUERY";
docker exec -it hiveserver /opt/hive/bin/beeline -u 'jdbc:hive2://root@hiveserver:10000/' -e "$DML_QUERY";
docker exec -it hiveserver /opt/hive/bin/beeline -u 'jdbc:hive2://root@hiveserver:10000/' -e "SELECT * FROM bdp.aircrafts_csv_table";