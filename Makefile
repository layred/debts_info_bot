.PHONY: dev-up dev-down dev-restart prod-up prod-down prod-restart migrate collectstatic

prod-up:
	docker compose -f docker-compose.prod.yml up -d --build

prod-down:
	docker compose -f docker-compose.prod.yml down

prod-restart:
	docker compose -f docker-compose.prod.yml down
	docker compose -f docker-compose.prod.yml up -d --build

dev-up:
	docker compose up -d --build

dev-down:
	docker compose down

dev-restart:
	docker compose down
	docker compose up -d --build

migrate:
	poetry run python ./src/manage.py makemigrations --noinput
	poetry run python ./src/manage.py migrate --noinput

collectstatic:
	poetry run python ./src/manage.py collectstatic --noinput
