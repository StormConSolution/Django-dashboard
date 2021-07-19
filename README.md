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

The project is deployed on production through a docker-compose file 
`docker-compose.yaml` in the root repository. This docker compose setup 
has 4 services:

* celery: task queue for the data when a csv is uploaded
* redis: used as broker by celery
* database: postgres database
* web: contains the django aplication and nginx server to serve the appo

Environment variables are defined in `.env` file.
HTTPS certificates must exist in the folder `./certificates`, this folder is
mapped to `/certificates` inside the `web` service, this certificates are
used by the nginx server´.

Firebase credentials should exist in the same folder as `docker-compose.yaml`
with the name `firebase-credentials.json`, this file is mapped to
`/firebase-credentials.json` inside the container so the `.env` file for production
should have the following line `GOOGLE_APPLICATION_CREDENTIALS=/firebase-credentials.json`

The `web` service uses the following image `repustate/dashboard:latest`
to build this image run `make build` and then push to the docker registry
with `make push`.

To test the docker build locally run `make up-compose`, this command uses
the file `docker-compose-test.yaml`, this docker compose file differs from
production by not using the HTTPS certificates.

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

### Assets build

Javascript graphs code is built using webpack, the source files are in `assets/js` and it produces one file `dashboard/static/assets/js/bundle.js`. Makefile has two commands for this:

```
# for development, it reloads on changes
webpack-dev:
	webpack -w

# build for production, it does things like minify the file
webpack-production:
	webpack --mode="production"
```