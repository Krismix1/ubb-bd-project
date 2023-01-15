FROM m8928/hadoop-base:3.2.2-java8

ENV TEZ_VERSION 0.10.2
ENV TEZ_URL https://archive.apache.org/dist/tez/${TEZ_VERSION}/apache-tez-${TEZ_VERSION}-bin.tar.gz

RUN curl -o tez-$TEZ_VERSION.tar.gz ${TEZ_URL}
RUN mkdir /opt/tez-$TEZ_VERSION
RUN tar -xvf /tez-$TEZ_VERSION.tar.gz -C /opt/tez-$TEZ_VERSION && rm /tez-$TEZ_VERSION.tar.gz
RUN ln -s /opt/tez-$TEZ_VERSION/apache-tez-${TEZ_VERSION}-bin /opt/tez

COPY tez-site.xml /etc/hadoop

ENV TEZ_CONF=/etc/hadoop
ENV TEZ_JARS=/opt/tez
ENV TEZ_CLASSPATH=${TEZ_CONF}:${TEZ_JARS}/*:${TEZ_JARS}/lib/*
ENV HADOOP_CLASSPATH=${HADOOP_CLASSPATH}:${TEZ_CLASSPATH}
