# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# This Dockerfile is used to build a Docker image for a Python application.
# It sets up a Python environment, installs dependencies using Poetry,
# and runs the application using uvicorn.

ARG PYTHON_VERSION=3.10.12
# Specifies the Python version to use as a build argument.

FROM python:${PYTHON_VERSION}-slim as base
# Sets the base image for the Dockerfile as a slim version of Python.

ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from writing pyc files.

ENV VENV_PATH=/venv
# Sets the path for the Python virtual environment.

ENV PYTHONUNBUFFERED=1
# Keeps Python from buffering stdout and stderr.

RUN python3 -m venv $VENV_PATH
# Creates a Python virtual environment.

RUN $VENV_PATH/bin/pip install -U pip setuptools
# Installs or upgrades pip and setuptools in the virtual environment.

RUN $VENV_PATH/bin/pip install poetry==1.8.2
# Installs Poetry in the virtual environment.

ENV PATH="/venv/bin:$PATH"
# Adds the virtual environment's bin directory to the PATH.

WORKDIR /app
# Sets the working directory in the container.

ARG UID=10001
# Specifies the UID for the non-privileged user.

RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser
# Creates a non-privileged user that the app will run under.

RUN --mount=type=cache,target=/root/.cache/poetry_dependencies \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    poetry config virtualenvs.create false \
    && poetry install --no-interaction
# Downloads dependencies using Poetry and installs them in the virtual environment.

RUN mkdir -p /home/appuser && chown -R appuser:appuser /home/appuser /app
# Creates a directory for the non-privileged user and sets ownership.

USER appuser
# Switches to the non-privileged user.

ENV POETRY_VIRTUALENVS_PATH=/app/.cache/pypoetry/virtualenvs
# Sets the environment variable for the path where Poetry will store virtual environments.

COPY . .
# Copies the source code into the container.

EXPOSE 8000
# Exposes the port that the application listens on.
ENV ENVIRONMENT=production

WORKDIR /app/
# Sets the working directory to /app/.

CMD ["uvicorn", "calarmhelp.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# Runs the application using uvicorn.
