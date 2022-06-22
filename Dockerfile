# syntax=docker/dockerfile:1.2

ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-slim

WORKDIR /casbin-tortoise
ENV PATH="/root/.local/bin:/casbin-tortoise/.venv/bin:${PATH}"

RUN apt-get update && \
    apt-get install --no-install-recommends -y curl build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /casbin-tortoise/
RUN poetry install

COPY . /casbin-tortoise

CMD [ "sleep", "infinity" ]
