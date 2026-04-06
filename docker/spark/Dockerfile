FROM apache/spark:3.5.1

USER root

RUN apt-get update && apt-get install -y \
    python3-pip \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install psycopg2-binary numpy

USER spark