# Multi-stage build para otimizar tamanho da imagem.
FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .

# Instalar dependências em cache layer
RUN pip install --user --no-cache-dir --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# Stage final - apenas com o necessário
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/scripts
ENV PORT=8080

WORKDIR /app

# Copiar apenas Python packages do builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copiar aplicação
COPY requirements.txt .
COPY app.py .
COPY scripts/ scripts/
COPY templates/ templates/
COPY static/ static/
COPY assets/ assets/
COPY data/ data/
COPY models/mmarco-reranker/ models/mmarco-reranker/

# Runtime deve carregar o reranker somente do disco, sem chamar o HF Hub.
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1
RUN python -c "from reranker import _get_reranker; _get_reranker(); print('Reranker local validado.')"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/').read()"

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers=1", "--threads=8", "--timeout=120", "--access-logfile", "-"]
