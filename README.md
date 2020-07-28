## How to use it

```bash
$ # Get the code
$ git clone git@bitbucket.org:repustatecom/dashboard.git
$ cd dashboard
$
$ # Virtualenv modules installation (Unix based systems)
$ virtualenv env
$ source env/bin/activate
$
$ # Virtualenv modules installation (Windows based systems)
$ # virtualenv env
$ # .\env\Scripts\activate
$
$ # Install modules - SQLite Storage
$ pip3 install -r requirements.txt
$
$ # Create tables
$ python manage.py makemigrations
$ python manage.py migrate
$
$ # Start the application (development mode)
$ python manage.py runserver # default port 8000
$
$ # Start the app - custom port
$ # python manage.py runserver 0.0.0.0:<your_port>
$
$ # Access the web app in browser: http://127.0.0.1:8000/
```

## Deployment

The app is provided with a basic configuration to be executed in [Docker](https://www.docker.com/), [Gunicorn](https://gunicorn.org/)

### [Docker](https://www.docker.com/) execution

---

The application can be easily executed in a docker container. The steps:

> Get the code

```bash
$ git clone git clone git@bitbucket.org:repustatecom/dashboard.git
$ cd dashboard
```

> Start the app in Docker

```bash
$ sudo docker-compose pull && sudo docker-compose build && sudo docker-compose up -d
```

> launching first time also run

```bash
$ sudo docker-compose exec repustate-app python3 manage.py migrate
```

Visit `http://localhost:5005` in your browser. The app should be up & running.

<br />

### [Gunicorn](https://gunicorn.org/)

---

Gunicorn 'Green Unicorn' is a Python WSGI HTTP Server for UNIX.

> Install using pip

```bash
$ pip install gunicorn
```

> Start the app using gunicorn binary

```bash
$ gunicorn --bind=0.0.0.0:8001 dashboard.wsgi:application
Serving on http://localhost:8001
```

Visit `http://localhost:8001` in your browser. The app should be up & running.

</br>

[Django Dashboard CoreUI](https://appseed.us/admin-dashboards/django-dashboard-coreui) - Provided by **AppSeed** [Web App Generator](https://appseed.us/app-generator).
