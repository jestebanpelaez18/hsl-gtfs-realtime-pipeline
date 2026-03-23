FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install dbt-postgres==1.8.0 psycopg2-binary

WORKDIR /app/dbt