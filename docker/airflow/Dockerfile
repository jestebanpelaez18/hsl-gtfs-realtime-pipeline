FROM apache/airflow:2.5.1

USER root

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    openjdk-11-jdk \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/lib/jvm/java-11-openjdk-$(dpkg --print-architecture) /usr/lib/jvm/java-11-openjdk
ENV JAVA_HOME="/usr/lib/jvm/java-11-openjdk"
ENV SPARK_HOME="/opt/spark"
ENV PATH="${JAVA_HOME}:${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}"

RUN mkdir -p ${SPARK_HOME} && \
    curl -L https://archive.apache.org/dist/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz -o spark.tgz && \
    tar xvzf spark.tgz --directory ${SPARK_HOME} --strip-components 1 && \
    rm -rf spark.tgz

RUN chown -R airflow ${SPARK_HOME}

COPY requirements.txt /requirements.txt

USER airflow
RUN python -m pip install --upgrade pip
RUN pip install --upgrade psycopg2-binary
RUN pip install --no-cache-dir -r /requirements.txt

COPY entrypoint.sh /entrypoint.sh
USER root
RUN chmod +x /entrypoint.sh
USER airflow

ENTRYPOINT ["/entrypoint.sh"]
