# syntax=docker/dockerfile:1

FROM python:3.7

WORKDIR /casbin-tortoise

RUN pip install -U pip setuptools wheel && \
    pip install pdm~=2.10.0

COPY pyproject.toml pyproject.toml

RUN pdm export -G :all --pyproject -o requirements.txt && \
    pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/casbin-tortoise

CMD [ "sleep", "infinity" ]
