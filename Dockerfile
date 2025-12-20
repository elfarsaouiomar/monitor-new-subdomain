FROM python:3.13.11

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python3","check-new-subdomain.py"]