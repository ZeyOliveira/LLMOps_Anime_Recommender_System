# 1. Imagem Base: Mantemos a versão 3.12-slim conforme sua necessidade [cite: 3]
FROM python:3.12-slim

# 2. Variáveis de Ambiente Industriais
# PYTHONDONTWRITEBYTECODE: Evita que o Python gere arquivos .pyc inúteis no container
# PYTHONUNBUFFERED: Garante que os logs apareçam em tempo real no terminal do Docker/K8s
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# 3. Dependências do Sistema
# Adicionamos 'git' caso alguma biblioteca do requirements venha direto do GitHub
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 4. Instalação de Dependências (Otimização de Cache) [cite: 4]
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Cópia Seletiva Profissional 
# Note que não copiamos a pasta 'arquivos_professor' ou '.env' (usamos o .dockerignore)
COPY app/ ./app/
COPY src/ ./src/
COPY pipelines/ ./pipelines/
COPY utils/ ./utils/
COPY config/ ./config/
COPY data/ ./data/

# 6. Exposição da porta do Streamlit
EXPOSE 8501

# 7. Healthcheck Industrial 
# Essencial para o Kubernetes saber quando reiniciar o container se ele travar
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 8. Comando de Execução
# Usamos o caminho absoluto e garantimos que o Streamlit escute em todas as interfaces (0.0.0.0)
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]