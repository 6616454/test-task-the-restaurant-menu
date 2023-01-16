up:
	docker compose -f docker-compose.yaml up --build

down:
	docker compose -f docker-compose.yaml down -v && docker network prune --force