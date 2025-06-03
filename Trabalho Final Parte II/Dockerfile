# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primeiro para cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante da aplicação
COPY . .

# Comando padrão (pode ser sobrescrito no docker-compose.yml)
# CMD ["python", "source.py"]