all:
	@echo "Starting the dev containers"
	docker compose -f docker-compose.yml build
	docker compose -f docker-compose.yml up -d

clean:
	@echo "Removing images, volumes & networks"
	docker compose -f docker-compose.yml down --rmi all -v

fclean: clean
	docker system prune -f

re: fclean all

logs:
	@echo "Tailing logs..."
	docker compose logs -f

trigger:
	@echo "Triggering DAG: gtfs_realtime_dag"
	docker compose exec airflow-webserver airflow dags trigger gtfs_realtime_dag

.PHONY: all clean fclean re logs trigger