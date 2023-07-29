FROM python:3.12.0b4

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python3","check-new-subdomain.py"]