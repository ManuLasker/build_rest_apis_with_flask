FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN apt-get update -y
RUN apt-get install gcc  build-essential -y
RUN apt-get update -y

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src  src
COPY wsgi.py wsgi.py
COPY uwsgi.ini uwsgi.ini