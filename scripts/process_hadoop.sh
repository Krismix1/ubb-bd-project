# find / -name 'hadoop-streaming*.jar'

docker cp project/hadoop/mapper.py namenode:/
docker cp project/hadoop/reducer.py namenode:/
output_dir="/aircraft_data_processed"

docker exec -it namenode \
  bash -c "hdfs dfs -rm -r ${output_dir}; hadoop jar /opt/hadoop-3.3.4/share/hadoop/tools/lib/hadoop-*streaming*.jar \
  -file /mapper.py    -mapper /mapper.py \
  -file /reducer.py   -reducer /reducer.py \
  -input /aircraft_data_json/part-*json -output ${output_dir}"

# https://www.michael-noll.com/tutorials/writing-an-hadoop-mapreduce-program-in-python/
