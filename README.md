# HSL GTFS Realtime Pipeline

This project is a data engineering pipeline built with **Apache Airflow** and **PySpark** to process real-time public transportation data from **HSL (Helsinki Regional Transport Authority)**.

The goal is to extract, transform, and load (ETL) GTFS Realtime data to enable insights about public transit patterns, vehicle delays, and overall system performance.

---

## Project Overview

- **Data Source**: [HSL Open Data](https://www.hsl.fi/en/open-data)
- **Pipeline Tools**: Apache Airflow, PySpark
- **Format**: GTFS Realtime (Protocol Buffers)
- **Purpose**: Learn and practice real-world data engineering using transit data

## Features

- Extracts data from HSL's GTFS Realtime feeds:
  - ✅ Vehicle Positions
  - ✅ Trip Updates
- Parses Protobuf into JSON using `gtfs-realtime-bindings`
- Stores clean data in `data/raw/`
- Fully automated with Apache Airflow
- Easily extendable (e.g. to Service Alerts, PySpark transforms)

---

## Tech Stack

- **Apache Airflow**
- **Docker & Docker Compose**
- **Python 3.7+**
- **gtfs-realtime-bindings**
- **Protobuf, JSON, REST APIs**

---

## Project Structure

```bash
hsl-gtfs-realtime-pipeline/
├── dags/              # Airflow DAGs
├── src/               # Core ETL logic (fetch → parse → save)
├── data/raw/          # Output JSON files
├── docker/airflow/    # Dockerfile + entrypoint
├── docker-compose.yml
├── requirements.txt
└── Makefile
```
---

## Installation

Follow these steps to set up and run the project using Docker and Docker Compose. The `Makefile` is provided to streamline the process.

### 1. Prerequisites

Make sure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Make](https://www.gnu.org/software/make/)

### 2. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/jestebanpelaez18/hsl-gtfs-realtime-pipeline.git
cd hsl-gtfs-realtime-pipeline
```

### 3. Build and Start the Project

Use the Makefile to handle the setup, build, and start processes. Run:

```bash
make
```
This command will:
- Build and start the Docker containers defined in docker-compose.yml
- Build and start Airflow
`
### 4. Visit Airflow UI

* URL: [http://localhost:8080](http://localhost:8080)
* Default login: `airflow / airflow`

### 5. Trigger the DAG

Manually in the UI or run:
```bash
make trigger
```
---

## Future Improvements

* Add support for **Service Alerts** feed
* Add PySpark transforms and analytics
* Schedule with cron-like intervals (`*/5 * * * *`)
* Export to database or cloud storage (Postgres, S3, BigQuery)