webpack-dev:
	npm run webpack-dev

webpack-production:
	npm run webpack

celery-web:
	celery -A dashboard flower --basic_auth=admin:admin

celery-worker:
	celery -A dashboard.celery worker --logfile celery.log

transfer-docker-compose:
	scp -i tmp/dashboard.pem docker-compose.yaml ubuntu@34.230.9.46:~/setup

# docker
build: webpack-production
	docker build -t repustate/dashboard:latest .
push:
	docker push repustate/dashboard:latest 
publish: build push
up-compose:
	docker-compose -f docker-compose-test.yaml up 
down-compose:
	docker-compose -f docker-compose-test.yaml down
exec-web:
	docker-compose -f docker-compose-test.yaml exec web bash

###
postgres-start:
	brew services start postgresql

postgres-stop:
	brew services stop postgresql
run:
	python3 manage.py runserver

	
