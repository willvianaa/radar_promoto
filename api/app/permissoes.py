"""Matriz de permissões (docs/05-matriz-permissoes.md), aplicada no servidor.

Decisões que a matriz deixa em aberto (confirmar com a mãe/DPO):
- CPF completo: RH, DP, Compliance e P&P (quem emite ou apura dossiê); demais veem mascarado.
- Admin é perfil técnico: não lê dado individual.
- Diretoria só vê agregado.
"""

from dataclasses import dataclass
from enum import StrEnum


class Perfil(StrEnum):
    DIRETORIA = "diretoria"
    RH = "rh"
    DP = "dp"
    COMPLIANCE = "compliance"
    PP = "pp"
    MERCH = "merch"
    GERENCIA = "gerencia_regional"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


_RAIO_X = {Perfil.RH, Perfil.DP, Perfil.COMPLIANCE, Perfil.PP, Perfil.MERCH, Perfil.GERENCIA, Perfil.SUPERVISOR}
_CPF_COMPLETO = {Perfil.RH, Perfil.DP, Perfil.COMPLIANCE, Perfil.PP}
_HUMOR_DETALHE = {Perfil.RH, Perfil.SUPERVISOR}
_HUMOR_ALERTA = {Perfil.GERENCIA, Perfil.PP}
_DOENTE = {Perfil.RH}
_MOTIVO_FALTA = {Perfil.RH, Perfil.DP}
_PARAM_ESCRITA = {Perfil.PP}
_AUDITORIA_COMPLETA = {Perfil.COMPLIANCE}
_AUDITORIA_PROPRIA = {Perfil.RH, Perfil.PP}
_UPLOAD = {"faltas": {Perfil.DP}, "estoque": {Perfil.PP, Perfil.MERCH}}  # matriz 5.3
_REPROCESSAR = {Perfil.PP}


@dataclass(frozen=True)
class Escopo:
    tipo: str  # nacional | regional | equipe
    valor: str = ""  # nome da regional; CPF do supervisor (equipe)
    rotulo: str = ""  # nome exibido

    def texto(self) -> str:
        return "nacional" if self.tipo == "nacional" else f"{self.tipo}:{self.rotulo}"


@dataclass(frozen=True)
class Acesso:
    perfil: Perfil
    escopo: Escopo

    def ver_raio_x(self) -> bool:
        return self.perfil in _RAIO_X

    def ver_cpf_completo(self) -> bool:
        return self.perfil in _CPF_COMPLETO

    def ver_humor_detalhe(self) -> bool:
        return self.perfil in _HUMOR_DETALHE

    def ver_humor_alerta(self) -> bool:
        return self.perfil in _HUMOR_DETALHE | _HUMOR_ALERTA

    def ver_doente(self) -> bool:
        return self.perfil in _DOENTE

    def ver_motivo_falta(self) -> bool:
        return self.perfil in _MOTIVO_FALTA

    def alterar_parametros(self) -> bool:
        return self.perfil in _PARAM_ESCRITA

    def auditoria(self) -> str | None:
        """'completa', 'propria' ou None (sem acesso)."""
        if self.perfil in _AUDITORIA_COMPLETA:
            return "completa"
        return "propria" if self.perfil in _AUDITORIA_PROPRIA else None

    def pode_upload(self, origem: str) -> bool:
        return self.perfil in _UPLOAD.get(origem, set())

    def pode_reprocessar(self) -> bool:
        return self.perfil in _REPROCESSAR


def escopo_do_usuario(perfil: str, regional: str | None, supervisor_cpf: str | None, supervisor_nome: str | None) -> Escopo:
    """Regional/equipe sem vínculo cadastrado recebe escopo vazio (não vê nada)."""
    if perfil == Perfil.GERENCIA:
        return Escopo("regional", regional or "", regional or "")
    if perfil == Perfil.SUPERVISOR:
        return Escopo("equipe", supervisor_cpf or "", supervisor_nome or "")
    return Escopo("nacional")


def no_escopo(escopo: Escopo, regional: str | None, supervisor_cpf: str | None) -> bool:
    if escopo.tipo == "nacional":
        return True
    if not escopo.valor:
        return False
    if escopo.tipo == "regional":
        return regional == escopo.valor
    return supervisor_cpf == escopo.valor


def mascara_cpf(cpf: str) -> str:
    """'12345678901' vira '***.456.789-**'. CPF provisório (nome normalizado) vira tudo mascarado."""
    if cpf.isdigit() and len(cpf) == 11:
        return f"***.{cpf[3:6]}.{cpf[6:9]}-**"
    return "***.***.***-**"


def formata_cpf(cpf: str) -> str:
    if cpf.isdigit() and len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return mascara_cpf(cpf)


def humor_visivel(acesso: Acesso, opcao: str) -> str | None:
    """O que o perfil pode ver do humor: a opção, 'Alerta de cuidado' ou nada."""
    if acesso.ver_humor_detalhe():
        if opcao == "Doente" and not acesso.ver_doente():
            return "Alerta de cuidado"
        return opcao
    return "Alerta de cuidado" if acesso.ver_humor_alerta() else None
