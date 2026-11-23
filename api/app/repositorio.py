"""Acesso a dados: interface + implementação Postgres (SQLAlchemy Core).

Os testes usam uma implementação em memória (tests/api/fakes.py). A de Postgres roda onde há banco.
Atenção: `senha_hash` ainda não existe em app.usuario (db/modelo.sql); ver PR de contrato.
"""

import json
from dataclasses import dataclass
from typing import Any, Protocol

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


@dataclass
class UsuarioRegistro:
    id: int
    email: str
    nome: str
    perfil: str
    senha_hash: str | None
    ativo: bool = True
    regional: str | None = None
    supervisor_cpf: str | None = None
    supervisor_nome: str | None = None


class Repositorio(Protocol):
    def usuario_por_email(self, email: str) -> UsuarioRegistro | None: ...
    def usuario_por_id(self, usuario_id: int) -> UsuarioRegistro | None: ...
    def gravar_auditoria(self, usuario_id: int | None, acao: str, recurso: str, recurso_id: str | None,
                         ip: str | None, detalhe: dict[str, Any] | None) -> None: ...


_SQL_USUARIO = """
SELECT u.id, u.email, u.nome, u.perfil, u.senha_hash, u.ativo, r.nome AS regional,
       u.escopo_supervisor_cpf AS supervisor_cpf, c.nome AS supervisor_nome
FROM app.usuario u
LEFT JOIN core.regional r ON r.id = u.escopo_regional_id
LEFT JOIN core.colaborador c ON c.cpf = u.escopo_supervisor_cpf
WHERE {filtro}
"""


class RepositorioPg:
    def __init__(self, engine: Engine):
        self.engine = engine

    @classmethod
    def de_url(cls, url: str) -> "RepositorioPg":
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return cls(create_engine(url, pool_pre_ping=True))

    def _usuario(self, filtro: str, valor: Any) -> UsuarioRegistro | None:
        with self.engine.connect() as cx:
            linha = cx.execute(text(_SQL_USUARIO.format(filtro=filtro)), {"v": valor}).mappings().first()
        return UsuarioRegistro(**linha) if linha else None

    def usuario_por_email(self, email: str) -> UsuarioRegistro | None:
        return self._usuario("lower(u.email) = lower(:v)", email)

    def usuario_por_id(self, usuario_id: int) -> UsuarioRegistro | None:
        return self._usuario("u.id = :v", usuario_id)

    def gravar_auditoria(self, usuario_id, acao, recurso, recurso_id, ip, detalhe) -> None:
        with self.engine.begin() as cx:
            cx.execute(
                text("INSERT INTO app.auditoria (usuario_id, acao, recurso, recurso_id, ip, detalhe) "
                     "VALUES (:u, :a, :r, :rid, CAST(:ip AS inet), CAST(:d AS jsonb))"),
                {"u": usuario_id, "a": acao, "r": recurso, "rid": recurso_id, "ip": ip,
                 "d": json.dumps(detalhe) if detalhe is not None else None},
            )
