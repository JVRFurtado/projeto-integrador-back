# Usar Python 3.12 slim
FROM python:3.12-slim

# Diretório do app
WORKDIR /app

# Instalar dependências do sistema necessárias para psycopg2-binary
RUN apt-get update && \
    apt-get install -y gcc libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o projeto
COPY . .

# Rodar criar_admin e uvicorn
CMD ["sh", "-c", "python criar_admin.py && uvicorn main:app --host 0.0.0.0 --port $PORT"]