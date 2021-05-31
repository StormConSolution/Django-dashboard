webpack-dev:
	npm run webpack-dev

webpack-production:
	npm run webpack

celery-web:
	celery -A dashboard flower

celery-worker:
	celery -A dashboard.celery worker
