"""API do Radar Promotor (contrato: api/openapi.yaml). Rotas entram por grupo, em PRs pequenos."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .rotas_auth import router as rotas_auth

app = FastAPI(
    title="Radar Promotor API",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url=None,
    redoc_url=None,
)


@app.exception_handler(HTTPException)
async def _http(_: Request, exc: HTTPException) -> JSONResponse:
    d = exc.detail if isinstance(exc.detail, dict) else {"codigo": "erro", "mensagem": str(exc.detail)}
    return JSONResponse(d, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def _validacao(_: Request, exc: RequestValidationError) -> JSONResponse:
    # Só o caminho e o tipo do erro: o valor enviado pode ser sensível (senha, CPF) e não vai na resposta.
    det = [f"{'.'.join(str(x) for x in e['loc'])}: {e['type']}" for e in exc.errors()]
    return JSONResponse({"codigo": "requisicao_invalida", "mensagem": "Requisição inválida.", "detalhes": det}, status_code=422)


@app.get("/api/v1/saude", tags=["auth"], summary="Verificação de saúde")
def saude() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(rotas_auth, prefix="/api/v1")
