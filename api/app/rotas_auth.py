"""/auth/login, /auth/logout, /auth/eu."""

import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, EmailStr

from . import seguranca
from .auditoria import Auditoria
from .config import Configuracao
from .deps import Sessao, erro, get_auditoria, get_cfg, get_repo, get_sessao, monta_sessao
from .repositorio import Repositorio

router = APIRouter(prefix="/auth", tags=["auth"])

_JANELA_S, _MAX_FALHAS = 900, 5
_falhas: dict[str, deque[float]] = defaultdict(deque)  # por IP; por processo (suficiente até haver proxy/Redis)


class LoginEntrada(BaseModel):
    email: EmailStr
    senha: str


def _chave(request: Request) -> str:
    return request.client.host if request.client else "?"


def _bloqueado(chave: str) -> bool:
    fila = _falhas[chave]
    while fila and time.monotonic() - fila[0] > _JANELA_S:
        fila.popleft()
    return len(fila) >= _MAX_FALHAS


def _usuario_json(s: Sessao) -> dict:
    u = s.usuario
    return {"id": u.id, "nome": u.nome, "email": u.email, "perfil": u.perfil, "escopo": s.acesso.escopo.texto()}


@router.post("/login")
def login(corpo: LoginEntrada, request: Request, resposta: Response, repo: Repositorio = Depends(get_repo),
          cfg: Configuracao = Depends(get_cfg), aud: Auditoria = Depends(get_auditoria)):
    chave = _chave(request)
    if _bloqueado(chave):
        raise erro(429, "muitas_tentativas", "Muitas tentativas. Aguarde alguns minutos.")
    usuario = repo.usuario_por_email(corpo.email)
    senha_ok = seguranca.verifica_senha(corpo.senha, usuario.senha_hash if usuario else None)
    if not (usuario and usuario.ativo and senha_ok):
        _falhas[chave].append(time.monotonic())
        aud.registrar(usuario.id if usuario else None, "login_falha", "sessao")  # sem e-mail no registro
        raise erro(401, "credenciais_invalidas", "E-mail ou senha inválidos.")
    _falhas.pop(chave, None)
    resposta.set_cookie(
        cfg.cookie_nome, seguranca.emite_sessao(cfg.segredo, usuario.id), max_age=cfg.sessao_horas * 3600,
        httponly=True, secure=True, samesite="strict", path="/",
    )
    aud.registrar(usuario.id, "login", "sessao")
    return _usuario_json(monta_sessao(usuario))


@router.post("/logout", status_code=204)
def logout(resposta: Response, cfg: Configuracao = Depends(get_cfg), sessao: Sessao = Depends(get_sessao),
           aud: Auditoria = Depends(get_auditoria)):
    aud.registrar(sessao.usuario.id, "logout", "sessao")
    resposta.delete_cookie(cfg.cookie_nome, path="/", httponly=True, secure=True, samesite="strict")
    resposta.status_code = 204


@router.get("/eu")
def eu(sessao: Sessao = Depends(get_sessao)):
    return _usuario_json(sessao)
