# Imagem do worker (agendador do ingestor, 05:00 America/Sao_Paulo). Contexto: raiz do repositório.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Sao_Paulo

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ingestor/ ./ingestor/

RUN useradd --create-home --uid 10001 app
USER app

CMD ["python", "-m", "ingestor.agendador"]
