FROM python:3.7-slim-buster

ENV POETRY_HOME=/etc/poetry PATH="${PATH}:/etc/poetry/bin"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install --no-install-recommends -y neovim curl && \
    apt-get autoremove --purge && \
    rm -rf /var/lib/apt/lists/*

COPY . /casbin-tortoise
WORKDIR /casbin-tortoise

# python dependencies (Poetry)
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 - && \
    source /etc/poetry/env && \
    poetry config virtualenvs.create false && \
    poetry install

ENTRYPOINT ["tail", "-f", "/dev/null"]