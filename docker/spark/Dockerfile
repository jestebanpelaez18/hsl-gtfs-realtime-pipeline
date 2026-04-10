FROM apache/spark:3.5.1

USER root

RUN apt-get update && apt-get install -y \
    python3-pip \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install psycopg2-binary numpy azure-storage-blob

# Download hadoop-azure connector and dependencies
RUN curl -L https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-azure/3.3.4/hadoop-azure-3.3.4.jar \
    -o /opt/spark/jars/hadoop-azure-3.3.4.jar && \
    curl -L https://repo1.maven.org/maven2/com/microsoft/azure/azure-storage/8.6.6/azure-storage-8.6.6.jar \
    -o /opt/spark/jars/azure-storage-8.6.6.jar && \
    curl -L https://repo1.maven.org/maven2/org/eclipse/jetty/jetty-util/9.3.24.v20180605/jetty-util-9.3.24.v20180605.jar \
    -o /opt/spark/jars/jetty-util-9.3.24.v20180605.jar && \
    curl -L https://repo1.maven.org/maven2/org/eclipse/jetty/jetty-util-ajax/9.3.24.v20180605/jetty-util-ajax-9.3.24.v20180605.jar \
    -o /opt/spark/jars/jetty-util-ajax-9.3.24.v20180605.jar

USER spark