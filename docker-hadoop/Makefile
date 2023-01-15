DOCKER_NETWORK = docker-hadoop_default
ENV_FILE = hadoop.env
current_branch := 3.2.2-java8
build:
	docker build -t m8928/hadoop-base:$(current_branch) ./base
	docker build -t m8928/hadoop-base-with-tez:$(current_branch) ./base_with_tez
	docker build -t m8928/hadoop-namenode:$(current_branch) ./namenode
	docker build -t m8928/hadoop-datanode:$(current_branch) ./datanode
	docker build -t m8928/hadoop-resourcemanager:$(current_branch) ./resourcemanager
	docker build -t m8928/hadoop-nodemanager:$(current_branch) ./nodemanager
	docker build -t m8928/hadoop-historyserver:$(current_branch) ./historyserver
	docker build -t m8928/hadoop-hiveserver:$(current_branch) ./hiveserver
push: 
        docker push m8928/hadoop-base:$(current_branch)
        docker push m8928/hadoop-base_with_tez:$(current_branch)
        docker push m8928/hadoop-namenode:$(current_branch)
        docker push m8928/hadoop-datanode:$(current_branch)
        docker push m8928/hadoop-resourcemanager:$(current_branch)
        docker push m8928/hadoop-nodemanager:$(current_branch)
        docker push m8928/hadoop-historyserver:$(current_branch)
        docker push m8928/hadoop-hiveserver:$(current_branch)
