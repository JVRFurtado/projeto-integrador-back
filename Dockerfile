# ---------------- BASE ----------------
FROM python:3.12-slim

# Evita problemas de log buffering
ENV PYTHONUNBUFFERED=1

# Diretório da aplicação
WORKDIR /app

# ---------------- DEPENDÊNCIAS SISTEMA ----------------
RUN apt-get update && \
    apt-get install -y gcc libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# ---------------- PYTHON DEPENDENCIES ----------------
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ---------------- APP ----------------
COPY . .

# ---------------- START ----------------
CMD ["sh", "-c", "python criar_admin.py && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]