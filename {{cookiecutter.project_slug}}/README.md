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

Run a command inside the docker container:

```bash
docker-compose run --rm backend [command]
docker-compose run --rm backend alembic upgrade head
```


Swagger Documentation
---------------------

Documentation available on

> <http://localhost:5000/docs>


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
