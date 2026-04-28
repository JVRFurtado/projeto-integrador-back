# Usar Python 3.12 slim
FROM python:3.12-slim

# Diretório do app
WORKDIR /app

# Instalar dependências do sistema para psycopg2 e build de pacotes
RUN apt-get update && \
    apt-get install -y gcc libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Atualizar pip e instalar dependências Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o projeto
COPY . .

# Rodar criar_admin e iniciar o servidor
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
