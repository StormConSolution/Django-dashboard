service nginx start
gunicorn --forward-allow-ips="*" dashboard.wsgi --preload --log-level=DEBUG
#celery -A dashboard.celery worker &
#celery -A dashboard flower

while true; do sleep 1d; done