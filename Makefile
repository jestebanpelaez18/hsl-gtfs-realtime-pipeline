all:
	@echo "Starting the dev containers"
	docker compose -f docker-compose.yaml build
	docker compose -f docker-compose.yaml up -d

clean:
	@echo "Removing containers, volumes & networks"
	docker compose -f docker-compose.yaml down --rmi all -v

fclean: clean
	docker system prune -f

re: fclean all

logs:
	@echo "Tailing logs..."
	docker compose logs -f

trigger:
	@echo "Triggering DAG: gtfs_realtime_dag"
	docker compose exec airflow-webserver airflow dags unpause gtfs_realtime_dag
	docker compose exec airflow-webserver airflow dags trigger gtfs_realtime_dag

spark-vehicle:
	@echo "Running Spark silver job for vehicle_positions"
	docker compose exec spark spark-submit \
		--jars /app/jars/postgresql-42.7.3.jar \
		/app/spark_jobs/02_vehicle_positions_silver.py

spark-trip:
	@echo "Running Spark silver job for trip_updates"
	docker compose exec spark spark-submit \
		--jars /app/jars/postgresql-42.7.3.jar \
		/app/spark_jobs/03_trip_updates_silver.py

check-vehicle:
	@echo "Checking vehicle_positions row count"
	psql postgresql://hsl_user:hsl_pass@localhost:5433/hsl_db -c "SELECT COUNT(*) FROM silver.vehicle_positions;"

check-trip:
	@echo "Checking trip_updates row count"
	psql postgresql://hsl_user:hsl_pass@localhost:5433/hsl_db -c "SELECT COUNT(*) FROM silver.trip_updates;"

dbt-run:
	@echo "Running dbt models (Gold layer)"
	docker compose exec dbt dbt run

dbt-test:
	@echo "Running dbt tests"
	docker compose exec dbt dbt test

dbt-debug:
	@echo "Checking dbt connection"
	docker compose exec dbt dbt debug

.PHONY: all clean fclean re logs trigger spark-vehicle spark-trip check-vehicle check-trip dbt-run dbt-test dbt-debug