# syntax=docker/dockerfile:1

FROM python:3.11

RUN pip install -U pip setuptools wheel && \
    pip install pdm

WORKDIR /casbin-tortoise
COPY pyproject.toml pdm.lock /casbin-tortoise
RUN pdm export -G :all -o requirements.txt --without-hashes && \
    pip install -r requirements.txt

COPY . ./casbin-tortoise

ENV PYTHONPATH=/casbin-tortoise

CMD [ "sleep", "infinity" ]
