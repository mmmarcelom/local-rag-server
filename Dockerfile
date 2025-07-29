# Usar imagem base mais específica e segura
FROM python:3.11-slim-bullseye

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Criar usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas requirements primeiro (para cache)
COPY requirements.txt ./

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código do projeto
COPY . .

# Definir variáveis de ambiente padrão (serão sobrescritas pelo docker-compose)
ENV PYTHONPATH=/app/src \
    ENVIRONMENT=production \
    DEBUG=false \
    SERVER_HOST=0.0.0.0 \
    SERVER_PORT=8000 \
    HF_HOME=/home/appuser/.cache/huggingface \
    TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface/transformers \
    HF_DATASETS_CACHE=/home/appuser/.cache/huggingface/datasets

# Criar diretório de cache para o Hugging Face
RUN mkdir -p /home/appuser/.cache/huggingface && \
    chown -R appuser:appuser /home/appuser/.cache

# Mudar propriedade dos arquivos para o usuário não-root
RUN chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para executar o servidor
CMD ["python", "src/server.py"] 