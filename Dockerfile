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
    --home "/nonexistent" \
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

RUN mkdir /appuser && chown -R appuser:appuser /app
# Creates a directory for the non-privileged user and sets ownership.

USER appuser
# Switches to the non-privileged user.

ENV POETRY_VIRTUALENVS_PATH=/app/.cache/pypoetry/virtualenvs
# Sets the environment variable for the path where Poetry will store virtual environments.

COPY . .
# Copies the source code into the container.

EXPOSE 8000
# Exposes the port that the application listens on.

WORKDIR /app/
# Sets the working directory to /app/.

CMD poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Runs the application using uvicorn.

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

#############################################################
# ARG PYTHON_VERSION=3.10.12
# FROM python:${PYTHON_VERSION}-slim as base

# # Prevents Python from writing pyc files.
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV VENV_PATH=/venv
# # Keeps Python from buffering stdout and stderr to avoid situations where
# # the application crashes without emitting any logs due to buffering.
# ENV PYTHONUNBUFFERED=1

# RUN python3 -m venv $VENV_PATH
# RUN $VENV_PATH/bin/pip install -U pip setuptools
# RUN $VENV_PATH/bin/pip install poetry==1.8.2

# ENV PATH="/venv/bin:$PATH"

# # RUN sudo apt update
# # RUN sudo apt install pipx
# # RUN pipx ensurepath
# # RUN sudo pipx ensurepath --global # optional to allow pipx actions with --global argument
# # RUN pipx install poetry=1.8.2


# # Set the working directory in the container.
# WORKDIR /app

# # Create a non-privileged user that the app will run under.
# # See https://docs.docker.com/go/dockerfile-user-best-practices/
# ARG UID=10001
# RUN adduser \
#     --disabled-password \
#     --gecos "" \
#     --home "/nonexistent" \
#     --shell "/sbin/nologin" \
#     --no-create-home \
#     --uid "${UID}" \
#     appuser


# # Download dependencies as a separate step to take advantage of Docker's caching.
# # Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# # Leverage a bind mount to requirements.txt to avoid having to copy them into
# # into this layer.
# RUN --mount=type=cache,target=/root/.cache/poetry_dependencies \
#     --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
#     poetry config virtualenvs.create false \
#     && poetry install --no-interaction
# #     # python -m pip install -r requirements.txt

# # RUN --mount=type=cache,target=/root/.cache/poetry_dependencies \
# #     --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
# #     poetry config virtualenvs.create false \
# #     && poetry install --no-interaction
#     # && poetry env remove python

# RUN mkdir /appuser && chown -R appuser:appuser /app

# # Switch to the non-privileged user to run the application.
# USER appuser

# # Set the environment variable for the path where Poetry will store virtual environments
# ENV POETRY_VIRTUALENVS_PATH=/app/.cache/pypoetry/virtualenvs

# # Copy the source code into the container.
# COPY . .

# # Expose the port that the application listens on.
# EXPOSE 8000

# WORKDIR /app/

# # Run the application.
# CMD poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000