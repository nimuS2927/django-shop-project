export COMPOSE_FILE := "docker-compose.local.yml"

## Just does not yet manage signals for subprocesses reliably, which can lead to unexpected behavior.
## Exercise caution before expanding its usage in production environments.
## For more information, see https://github.com/casey/just/issues/2473 .


# Default command to list all available commands.
default:
    @just --list

# merge: Merge environment dotenv files into .env
# Usage: just merge prod or just merge local
merge +env_type:
    @echo "Merging '{{env_type}}' environment dotenv files into .env..."
    @python merge_production_dotenvs_in_dotenv.py {{env_type}}
    @echo "Merge completed."

# build-local: Build local containers
build-local *args:
	@docker compose -f docker-compose.local.yml build --no-cache {{args}}

# build-prod: Build production containers
build-prod *args:
	@docker compose -f docker-compose.production.yml build --no-cache {{args}}

# build-docs: Build docs containers
build-docs *args:
	@docker compose -f docker-compose.docs.yml build --no-cache {{args}}

# up-local: Start local containers
up-local:
    @docker compose -f docker-compose.local.yml up -d --remove-orphans

# up-prod: Start production containers
up-prod:
    @docker compose -f docker-compose.production.yml up -d --remove-orphans

# up-docs: Start docs containers
up-docs:
    @docker compose -f docker-compose.docs.yml up -d --remove-orphans

# down: Stop containers.
down:
    @echo "Stopping containers..."
    @docker compose down

# prune: Remove containers and their volumes.
prune *args:
    @echo "Killing containers and removing volumes..."
    @docker compose down -v {{args}}

# logs: View container logs
logs *args:
    @docker compose logs -f {{args}}

# manage: Executes `manage.py` command.
manage +args:
    @docker compose run --rm django python ./manage.py {{args}}

# Экспортируем зависимости из poetry в requirements/
export-reqs:
    poetry export -f requirements.txt --without-hashes --without dev --without prod -o requirements/base.txt
    poetry export -f requirements.txt --without-hashes --with prod -o requirements/production.txt
    poetry export -f requirements.txt --without-hashes --with dev --with prod -o requirements/local.txt
