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

up-compose:
	docker-compose -f docker-compose-test.yaml up 
down-compose:
	docker-compose -f docker-compose-test.yaml down
exec-web:
	docker-compose -f docker-compose-test.yaml exec web bash


transfer-docker-compose:
	scp -i ~/Downloads/dashboard.pem docker-compose.yaml ubuntu@34.230.9.46:~/setup
	