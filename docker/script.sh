service nginx start
gunicorn --forward-allow-ips="*" dashboard.wsgi --preload --log-level=DEBUG --workers=4 --timeout 300
#python3 manager.py runserver 0.0.0.0:8000
#celery -A dashboard.celery worker &
#celery -A dashboard flower

while true; do sleep 1d; done