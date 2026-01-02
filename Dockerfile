FROM python:3.11-slim

LABEL org.opencontainers.image.title="Monitor New Subdomain"
LABEL org.opencontainers.image.description="Open-source tool to monitor new subdomains using multiple OSINT sources"
LABEL org.opencontainers.image.authors="Omar El Farsaoui <https://github.com/elfarsaouiomar>"
LABEL org.opencontainers.image.url="https://github.com/elfarsaouiomar/monitor-new-subdomain"
LABEL org.opencontainers.image.source="https://github.com/elfarsaouiomar/monitor-new-subdomain"
LABEL org.opencontainers.image.documentation="https://github.com/elfarsaouiomar/monitor-new-subdomain#readme"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.version="1.0"
LABEL org.opencontainers.image.vendor="elfarsaouiomar"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]