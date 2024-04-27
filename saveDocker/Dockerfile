# Use an official Python runtime as a parent image
FROM python:3.10.12-slim

# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Install Poetry
RUN pip install poetry==1.8.2

# Set the working directory in the container
WORKDIR /app

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock* /app/

# Project initialization:
# --no-root: Don't install the current project package (since it's not copied yet)
# --no-dev: Skip development dependencies (if applicable)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev

# Copying the rest of the application
COPY . /app

# Command to run the application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
CMD ["poetry", "run", "start"]
