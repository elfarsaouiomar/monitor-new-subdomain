FROM python:3.14.1

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python3","check-new-subdomain.py"]