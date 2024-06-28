FROM python:3.11.0
LABEL maintainer="deimandar"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

COPY requirements.txt /temp/requirements.txt
COPY main /main

WORKDIR /main
EXPOSE 8000
EXPOSE 6379
EXPOSE 5555
EXPOSE 5432

RUN pip install --upgrade pip  && pip install -r /temp/requirements.txt


ENV PATH="/venv/bin:$PATH"

USER root

