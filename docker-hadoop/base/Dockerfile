FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 \
      apt-utils \
      locales \
      tzdata \
      openjdk-8-jdk \
      net-tools \
      curl \
      netcat \
      gnupg \
      libsnappy-dev \
      vim \
      iputils-ping \
      rename \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
      
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64

RUN curl -O https://dist.apache.org/repos/dist/release/hadoop/common/KEYS

RUN gpg --import KEYS

ENV HADOOP_VERSION 3.3.4
ENV HADOOP_URL https://www.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz

RUN set -x \
    && curl -fSL "$HADOOP_URL" -o /tmp/hadoop.tar.gz \
    && curl -fSL "$HADOOP_URL.asc" -o /tmp/hadoop.tar.gz.asc \
    && gpg --verify /tmp/hadoop.tar.gz.asc \
    && tar -xvf /tmp/hadoop.tar.gz -C /opt/ \
    && rm /tmp/hadoop.tar.gz*

RUN ln -s /opt/hadoop-$HADOOP_VERSION/etc/hadoop /etc/hadoop

RUN mkdir /opt/hadoop-$HADOOP_VERSION/logs

RUN mkdir /hadoop-data

ENV HADOOP_HOME=/opt/hadoop-$HADOOP_VERSION
ENV HADOOP_CONF_DIR=/etc/hadoop
ENV HADOOP_CLASSPATH=/etc/hadoop:/opt/hadoop-$HADOOP_VERSION/share/hadoop/common/lib/*:/opt/hadoop-$HADOOP_VERSION/share/hadoop/common/*:/opt/hadoop-$HADOOP_VERSION/share/hadoop/hdfs:/opt/hadoop-$HADOOP_VERSION/share/hadoop/hdfs/lib/*:/opt/hadoop-$HADOOP_VERSION/share/hadoop/hdfs/*:/opt/hadoop-$HADOOP_VERSION/share/hadoop/mapreduce/lib/*:/opt/hadoop-$HADOOP_VERSION/share/hadoop/mapreduce/*:/opt/hadoop-$HADOOP_VERSION/share/hadoop/yarn:/opt/hadoop-$HADOOP_VERSION/share/hadoop/yarn/lib/*:/opt/hadoop-$HADOOP_VERSION/share/hadoop/yarn/*
ENV MULTIHOMED_NETWORK=1
ENV USER=root
ENV PATH $HADOOP_HOME/bin/:$PATH

ADD entrypoint.sh /entrypoint.sh

RUN chmod a+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
