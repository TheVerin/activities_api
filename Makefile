# Dev stage

# Build docker image on base settings
build:
	docker-compose build

# Run app on dev settings with migrations and creating premium group
setup:
	docker-compose build
	docker-compose up -d
	docker-compose exec django python manage.py makemigrations
	docker-compose exec django python manage.py migrate
	docker-compose exec django python manage.py collectstatic


# Set up containers on dev settings then test and if tests pass stop and remove all containers.
test:
	docker-compose run --rm django coverage run --source='.' manage.py test && black --check --diff . && flake8 && mypy .

# Remove running containers
remove:
	docker-compose down -v

# Format code
format:
	docker-compose run --rm django black .

# Run linter
lint:
	docker-compose run --rm django black --check --diff . && flake8 && mypy .