FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python criar_admin.py && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]