FROM python:3.11.0
ENV PYTHONDONTWRITEBYTECODE = 1
ENV PYTHONBUFFERED = 1
WORKDIR /main
COPY . .
RUN python -m pip install --upgrade pip &&  \
    pip install -r requirements.txt

WORKDIR /main/main
