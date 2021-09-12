# A development Dockerfile
#
# Useful for in-container development. Relies on the fact that Docker Compose
# will map volumes with the application source code from the host to the
# container, so the developed package can be easily changed, while isolating
# the environment.

# Dependency compilation stage
FROM python:3.9.4-slim-buster as compile-image

ARG APP_USER=app_user
ARG APP_USER_HOME=/home/$APP_USER
ARG APP_DIR=$APP_USER_HOME/app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	build-essential \
	gcc \
	libpq-dev \
	python-dev

WORKDIR $APP_DIR

# Setup the virtual environment first, since it does not change as often as the
# app requirements
RUN python3 -m venv venv

COPY ./requirements/full.txt ./requirements.txt

RUN venv/bin/pip install -U pip \
	&& venv/bin/pip install -r requirements.txt

COPY ./alembic.ini ./alembic.ini
# `setup.py` is required to install the project in editable state until pip
# supports PEP 660: Editable installs for `pyproject.toml` based builds
# COPY ./pyproject.toml ./pyproject.toml
COPY ./setup.py ./setup.py
COPY ./alembic/ ./alembic/
COPY ./tests/ ./tests/
COPY ./src ./src

# Final build stage
FROM python:3.9.4-slim-buster as build-image

ARG APP_USER=app_user
ARG APP_USER_HOME=/home/$APP_USER
ARG APP_DIR=$APP_USER_HOME/app

# Runtime should be isolated in a separate non-root user
RUN adduser --disabled-password --gecos "" $APP_USER
# Use the home directory for convenience
WORKDIR $APP_DIR
RUN chown -R $APP_USER:$APP_USER .
# Runtime depends on libpq shared objects
RUN apt-get update \
	&& apt-get install -y --no-install-recommends libpq-dev

COPY --from=compile-image --chown=$APP_USER $APP_DIR ./

# Installing the project in editable state allows overriding application source
# code via Docker Compose volume maps
RUN ./venv/bin/pip install -e .

# Switch to the non-root user
USER $APP_USER

ENV PATH="$APP_DIR/venv/bin:$PATH"
ENTRYPOINT ["alembic"]
