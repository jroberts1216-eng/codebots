FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./
COPY sql/merges/merge_dim_case.sql /app/sql/merges/merge_dim_case.sql

ENTRYPOINT ["python", "/app/main.py"]
