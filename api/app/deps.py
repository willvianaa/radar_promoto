"""Dependências do FastAPI: repositório, usuário autenticado e acesso (perfil + escopo)."""

from dataclasses import dataclass
from functools import lru_cache

from fastapi import Depends, HTTPException, Request

from . import seguranca
from .auditoria import Auditoria
from .config import Configuracao, configuracao
from .permissoes import Acesso, Perfil, escopo_do_usuario
from .repositorio import Repositorio, RepositorioPg, UsuarioRegistro


@lru_cache
def _repo_padrao() -> Repositorio:
    cfg = configuracao()
    if not cfg.database_url:
        raise RuntimeError("DATABASE_URL não definido")
    return RepositorioPg.de_url(cfg.database_url)


def get_repo() -> Repositorio:
    return _repo_padrao()


def get_cfg() -> Configuracao:
    return configuracao()


def erro(status: int, codigo: str, mensagem: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"codigo": codigo, "mensagem": mensagem})


@dataclass
class Sessao:
    usuario: UsuarioRegistro
    acesso: Acesso


def monta_sessao(usuario: UsuarioRegistro) -> Sessao:
    escopo = escopo_do_usuario(usuario.perfil, usuario.regional, usuario.supervisor_cpf, usuario.supervisor_nome)
    return Sessao(usuario, Acesso(Perfil(usuario.perfil), escopo))


def get_sessao(request: Request, repo: Repositorio = Depends(get_repo), cfg: Configuracao = Depends(get_cfg)) -> Sessao:
    token = request.cookies.get(cfg.cookie_nome)
    uid = seguranca.le_sessao(cfg.segredo, token, cfg.sessao_horas * 3600) if token else None
    usuario = repo.usuario_por_id(uid) if uid is not None else None
    if usuario is None or not usuario.ativo:  # desligado perde o acesso na hora (matriz 5.5)
        raise erro(401, "nao_autenticado", "Sessão ausente, expirada ou inválida.")
    return monta_sessao(usuario)


def get_auditoria(request: Request, repo: Repositorio = Depends(get_repo)) -> Auditoria:
    return Auditoria(repo, request.client.host if request.client else None)
