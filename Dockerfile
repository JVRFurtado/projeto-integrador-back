# Usar Python 3.12 (ou outra versão estável)
FROM python:3.12-slim

# Diretório do app
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o projeto
COPY . .

# Rodar migrations ou criar admin automaticamente
# Aqui chamamos o script criar_admin.py antes do uvicorn
CMD python criar_admin.py && uvicorn main:app --host 0.0.0.0 --port $PORT