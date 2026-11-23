"""Peças comuns dos fluxos de download: credenciais por ambiente, bloqueios, fatiamento.

Regras duras: não contorna captcha nem 2FA (para e levanta `BloqueioOrigem`); senha só de variável de
ambiente (secret); nada de credencial, URL real ou conteúdo de página em log.
"""

from __future__ import annotations

import datetime as dt
import os
from dataclasses import dataclass, field
from pathlib import Path

# Sinais de captcha/2FA: ao ver qualquer um, o fluxo para. Nunca tentar resolver.
SINAIS_BLOQUEIO = (
    'iframe[src*="captcha" i]',
    ".g-recaptcha",
    "[data-captcha]",
    'input[name="otp"]',
    'input[autocomplete="one-time-code"]',
)


class BloqueioOrigem(Exception):
    """Captcha, 2FA ou bloqueio na origem: parar a carga daquela origem e alertar."""


class ErroLogin(Exception):
    """Credencial recusada ou painel não apareceu após o login."""


class CredenciaisAusentes(Exception):
    pass


@dataclass(frozen=True)
class Credenciais:
    url: str
    usuario: str = field(repr=False)
    senha: str = field(repr=False)

    @classmethod
    def do_ambiente(cls, origem: str, env: dict[str, str] | None = None) -> Credenciais:
        """Lê INGESTOR_<ORIGEM>_URL / _USUARIO / _SENHA (secrets). `origem`: MONITORAMENTO ou 2PRT."""
        env = os.environ if env is None else env
        pre = f"INGESTOR_{origem.upper()}_"
        valores = {k: env.get(pre + k, "") for k in ("URL", "USUARIO", "SENHA")}
        faltam = [pre + k for k, v in valores.items() if not v]
        if faltam:
            raise CredenciaisAusentes("variáveis ausentes: " + ", ".join(faltam))
        return cls(valores["URL"].rstrip("/"), valores["USUARIO"], valores["SENHA"])


def checar_bloqueio(page) -> None:
    for seletor in SINAIS_BLOQUEIO:
        if page.locator(seletor).count():
            raise BloqueioOrigem("a origem pediu captcha ou segundo fator; carga interrompida")


def login(page, cred: Credenciais) -> None:
    """Formulário de login padrão (usuário de serviço). Para se aparecer captcha/2FA."""
    page.goto(cred.url + "/login")
    checar_bloqueio(page)
    page.fill('input[name="usuario"]', cred.usuario)
    page.fill('input[name="senha"]', cred.senha)
    page.click('button[type="submit"]')
    page.wait_for_load_state()
    checar_bloqueio(page)
    if not page.locator("#painel").count():
        raise ErroLogin("login não concluiu (credencial recusada ou layout alterado)")


def fatiar_periodo(ini: dt.date, fim: dt.date, dias: int) -> list[tuple[dt.date, dt.date]]:
    """Divide [ini, fim] (inclusivo) em janelas de até `dias` dias."""
    if dias < 1 or fim < ini:
        raise ValueError("período ou tamanho de fatia inválido")
    janelas, atual = [], ini
    while atual <= fim:
        fim_j = min(atual + dt.timedelta(days=dias - 1), fim)
        janelas.append((atual, fim_j))
        atual = fim_j + dt.timedelta(days=1)
    return janelas


def meses(ini: dt.date, fim: dt.date) -> list[tuple[dt.date, dt.date]]:
    """Janelas por mês-calendário cobrindo [ini, fim] (o 2PRT filtra por mês)."""
    out, atual = [], ini
    while atual <= fim:
        prox = (atual.replace(day=1) + dt.timedelta(days=32)).replace(day=1)
        out.append((atual, min(prox - dt.timedelta(days=1), fim)))
        atual = prox
    return out


def pasta_raw(env: dict[str, str] | None = None) -> Path:
    """Storage `raw` (único lugar onde export baixado pode ficar)."""
    env = os.environ if env is None else env
    p = Path(env.get("INGESTOR_STORAGE_RAW", "storage/raw"))
    p.mkdir(parents=True, exist_ok=True)
    return p
