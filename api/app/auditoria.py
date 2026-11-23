"""Auditoria append-only (app.auditoria; o banco bloqueia UPDATE/DELETE por trigger).

Regra: o registro guarda quem, o quê e qual recurso (id opaco), nunca CPF completo, humor ou motivo de falta.
Se a gravação falhar, a operação auditada falha junto (não há leitura individual sem rastro).
"""

from typing import Any

from .repositorio import Repositorio

ACOES = {
    "login", "login_falha", "logout",
    "leitura_raio_x", "dossie_criado", "dossie_editado", "dossie_emitido", "dossie_download",
    "parametro_criado", "ingestao_upload", "consulta_auditoria",
}
_PROIBIDAS = {"cpf", "senha", "email", "humor", "motivo", "opcao"}


class Auditoria:
    def __init__(self, repo: Repositorio, ip: str | None):
        self.repo = repo
        self.ip = ip

    def registrar(self, usuario_id: int | None, acao: str, recurso: str, recurso_id: str | None = None,
                  detalhe: dict[str, Any] | None = None) -> None:
        if acao not in ACOES:
            raise ValueError(f"ação de auditoria desconhecida: {acao}")
        if detalhe and _PROIBIDAS & {k.lower() for k in detalhe}:
            raise ValueError("detalhe de auditoria não pode conter dado pessoal ou sensível")
        self.repo.gravar_auditoria(usuario_id, acao, recurso, recurso_id, self.ip, detalhe)
