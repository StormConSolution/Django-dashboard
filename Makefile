webpack-dev:
	npm run webpack-dev

webpack-production:
	npm run webpack

celery-web:
	celery -A dashboard flower

celery-worker:
	celery -A dashboard.celery worker

build:
	docker build -t test .

remove:
	docker stop test
	docker rm test

start:
	docker run -td --name test -p 8080:80  test

compose:
	docker-compose -f docker-compose-new.yaml up -d
	