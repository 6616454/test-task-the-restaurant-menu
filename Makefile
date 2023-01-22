up:
	docker compose -f docker-compose.yaml up --build

down:
	docker compose -f docker-compose.yaml down -v && docker network prune --force

up-tests:
	docker compose -f docker-compose-test.yaml up --build

down-tests:
	docker compose -f docker-compose-test.yaml down -v && docker network prune --force


