FROM python:3.12.0rc2

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python3","check-new-subdomain.py"]