FROM python:3.12.0

WORKDIR /app

# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

ADD . /app

RUN pip install -r requirements.txt
