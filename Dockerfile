FROM python:3.12.0a5

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD . /app

ENTRYPOINT ["python3","check-new-subdomain.py"]