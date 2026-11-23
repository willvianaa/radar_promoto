# Imagem do serviço migrate (alembic upgrade head). Contexto de build: raiz do repositório.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Sao_Paulo

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# db/ (migrações e SQL) e regras/ (parâmetros usados pela migração 0002)
COPY db/ ./db/
COPY regras/ ./regras/

RUN useradd --create-home --uid 10001 app
USER app

CMD ["alembic", "-c", "db/alembic.ini", "upgrade", "head"]
