FROM python:3.9-slim

WORKDIR /app

RUN pip install prometheus_client

COPY metrics.py .

CMD ["python3", "metrics.py"]
