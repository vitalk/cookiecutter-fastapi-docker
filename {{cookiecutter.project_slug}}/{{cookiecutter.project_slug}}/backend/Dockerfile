FROM python:3.11.4

ENV PYTHONUNBUFFERED=1 PYTHONPATH=.

WORKDIR /{{cookiecutter.project_slug}}

COPY poetry.lock pyproject.toml alembic.ini /{{cookiecutter.project_slug}}/
RUN pip install -U pip && \
    pip install poetry && \
    poetry config virtualenvs.create false

ARG POETRY_INSTALL_DEV=false
RUN if [ "$POETRY_INSTALL_DEV" = "true" ]; then poetry install --with dev ; else poetry install --only main ; fi

COPY ./src /{{cookiecutter.project_slug}}/src

RUN useradd -m -d /{{cookiecutter.project_slug}} -s /bin/bash app && \
    chown -R app:app /{{cookiecutter.project_slug}}

USER app
