{{cookiecutter.project_name}}
=============================

{{cookiecutter.project_short_description}}


Development Requirements
------------------------

- Python 3.11
- Pip
- Poetry


Installation
------------

```bash
cp {{cookiecutter.project_slug}}/backend/{example.env,.env}
cp {{cookiecutter.project_slug}}/pg/{example.env,.env}
```

```bash
docker-compose up
```

It's possible to install `dev` dependencies via `--build-arg POETRY_INSTALL_DEV=true`

```
docker-compose build --build-arg "POETRY_INSTALL_DEV=true"
docker-compose up
```

Run a command inside the docker container:

```bash
docker-compose run --rm backend [command]
docker-compose run --rm backend alembic upgrade head
```


Swagger Documentation
---------------------

Documentation available on

> <http://localhost:{{cookiecutter.docker_image_backend_port}}/docs>


Testing
-------

Create database for your test suite

```
docker-compose run pg psql -U {{cookiecutter.pg_user}} -h {{cookiecutter.docker_image_pg}} {{cookiecutter.pg_db}} -c 'create database {{cookiecutter.pg_db}}_test'
```

Update `.env` to use correct `TEST_PG_DSN` if needed

```
docker-compose run --rm backend pytest
```

To run Ruff as a linter

```
docker-compose run --rm backend ruff check .
```


Project structure
-----------------

Files related to application are in the `src` directory.

```bash
% tree
.
├── README.md
├── docker-compose.yml
└── we_make_awesome_app
    ├── backend
    │   ├── Dockerfile
    │   ├── alembic.ini
    │   ├── example.env
    │   ├── poetry.lock
    │   ├── pyproject.toml
    │   └── src
    │       ├── api
    │       │   └── rest
    │       │       └── v0
    │       │           ├── health_check
    │       │           │   └── routes.py
    │       │           └── routes.py
    │       ├── config
    │       │   ├── config.py
    │       │   └── environment.py
    │       ├── infra
    │       │   ├── application
    │       │   │   ├── factory.py
    │       │   │   ├── pre_flight_check.py
    │       │   │   └── setup
    │       │   │       ├── cors.py
    │       │   │       ├── logging.py
    │       │   │       ├── sentry.py
    │       │   │       └── tracing.py
    │       │   └── database
    │       │       ├── declarative_base.py
    │       │       ├── migrations
    │       │       │   ├── env.py
    │       │       │   ├── script.py.mako
    │       │       │   └── versions
    │       │       ├── models.py
    │       │       └── session.py
    │       ├── main.py
    │       └── service
    │           └── health_check
    │               ├── dto.py
    │               └── service.py
    ├── pg
    │   └── example.env
    └── uvicorn
        └── config.json
```



Deployment
----------

On production environment to take advantage of multi-core CPUs the recommended
way is to use <i>gunicorn</i> as process manager with <i>uvicorn</i> worker, e.g.

```
gunicorn src.main:create_app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

Enjoy!

