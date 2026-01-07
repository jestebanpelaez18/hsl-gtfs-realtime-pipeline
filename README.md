# HSL GTFS Realtime Pipeline

This project is a data engineering pipeline built with **Apache Airflow**, **PySpark**, and **Databricks** to process real-time public transportation data from **HSL (Helsinki Regional Transport Authority)**.

The goal is to extract, clean, transform, and load (ETL) GTFS Realtime data to enable insights about public transit patterns, vehicle delays, and system performance.  
The pipeline follows a modern data lake architecture using **Delta Lake**.

---
## Project Architecture

```mermaid
graph LR
    A[HSL API GTFS] -->|Extract & Parse| B(Apache Airflow)
    B -->|Save JSON| C[Raw Data / Workspace]
    C -->|Hybrid Ingestion (Python/Pandas)| D[Databricks Spark Cluster]
    D -->|Transform & Clean| E[(Delta Lake Silver Table)]
    E -->|Analysis & Visualization| F[Databricks Notebooks]
```
**Note on Infrastructur**e: This project is deployed on **Databricks Community Edition**. Due to network/mounting restrictions in the free tier, the pipeline uses a custom local file ingestion strategy (Python os + Pandas) to bridge the gap between raw data upload and Spark processing, simulating a cloud storage m

---

## Project Overview

- **Data Source**: [HSL Open Data](https://www.hsl.fi/en/open-data)
- **Pipeline Tools**: Apache Airflow, PySpark, Databricks, Delta Lake
- **Format**: GTFS Realtime (Protocol Buffers → JSON)
- **Purpose**: Learn and practice real-world data engineering using public transit data

## Features

### Extraction (Airflow)
- Fetches GTFS Realtime feeds:
  - **Vehicle Positions**
  - **Trip Updates**
- Parses Protobuf (`.pb`) into JSON using `gtfs-realtime-bindings`
- Stores raw data under `data/raw/`
- Containerized with **Docker + Docker Compose**

### Transformation (Databricks + PySpark + Delta Lake)
A dedicated Databricks transformation layer processes the extracted JSON using a **hybrid reading approach**:

- **Dynamic File Detection**: Uses Python `os` library to detect the latest uploaded file in the Workspace.
- **Robust Ingestion**: Reads JSON via **Pandas** first to handle complex nested structures and bypass file system locks, then converts to Spark DataFrame.
- **Data Cleaning**:
  - Extracts nested fields (`vehicle`, `trip`, `position`)
  - Converts UNIX timestamps into proper Spark timestamps
  - Cleans coordinates and removes duplicates
- **Storage**: Loads cleaned data into a **Delta Lake Silver table** (`hsl_demo.vehicle_positions_silver`) partitioned by `event_date`.

---

## Tech Stack

- **Apache Airflow**
- **PySpark**
- **Databricks (Free Edition)**
- **Delta Lake**
- **Docker & Docker Compose**
- **Python 3.7+**
- **gtfs-realtime-bindings**
- **Protobuf, JSON, REST APIs**

---

## Project Structure

```bash
hsl-gtfs-realtime-pipeline/
├── dags/                     # Airflow DAGs
├── src/                      # Core extraction logic
├── data/raw/                 # Raw GTFS data exported by Airflow
├── databricks/               # PySpark notebooks (Delta Lake processing)
│   └── 01_vehicle_positions_cleaning.ipynb
├── docs/                     # Project documentation
│   └── databricks_01_vehicle_positions.md
├── docker/airflow/           # Airflow Dockerfile + entrypoint
├── docker-compose.yaml
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
* Default login: `admin / admin`

### 5. Trigger the DAG

Manually in the UI or run:
```bash
make trigger
```

### 6. Databricks Transformation Layer (Silver) 🥈

1. Upload the JSON file generated in `data/raw/` to your Databricks Workspace.
2. Run the `01_vehicle_positions_cleaning.ipynb` notebook.
3. The logic will automatically pick up the latest file, process it, and save it as a **Delta Table**.

---

## Future Improvements

* **Cloud Integration**: Migrate manual file ingestion to automated cloud storage mounting (Azure Blob Storage / S3) once a Standard Cluster is available.
* **Service Alerts**: Add support for the Service Alerts feed.
* **Medallion Architecture**: Complete the pipeline with Bronze (Raw Ingestion) and Gold (Aggregated Analytics) layers.
* **Automation**: Schedule Databricks jobs via Airflow `DatabricksSubmitRunOperator`.