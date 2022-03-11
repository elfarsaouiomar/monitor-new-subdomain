FROM python:3.11.0a5

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python3","check-new-subdomain.py"]