"""API do Radar Promotor. Nesta etapa expõe apenas a verificação de saúde.

As demais rotas seguem `api/openapi.yaml` e entram pela Onda 2 (feat/api).
"""

from fastapi import FastAPI

app = FastAPI(
    title="Radar Promotor API",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url=None,
    redoc_url=None,
)


@app.get("/api/v1/saude", tags=["auth"], summary="Verificação de saúde")
def saude() -> dict[str, str]:
    return {"status": "ok"}
