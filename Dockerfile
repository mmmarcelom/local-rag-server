FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas requirements primeiro (para cache)
COPY requirements.txt ./

# Instalar dependências Python com cache otimizado
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código do projeto
COPY . .

# Definir PYTHONPATH
ENV PYTHONPATH=/app/src

# Expor porta
EXPOSE 8000

# Comando para executar o servidor
CMD ["python", "src/server.py"] 