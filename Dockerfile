FROM python:3.12.0b4

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

ADD . /app

ENTRYPOINT ["python3","check-new-subdomain.py"]