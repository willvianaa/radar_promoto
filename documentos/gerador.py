"""Interface da geração: gerar_dossie(conteudo, perfil, dados) -> Arquivos.

Ordem: valida o contrato, revisa termos, decide a seção de contexto pelo perfil,
monta PDF e Excel e calcula SHA-256. Não grava nada: quem chama (API) guarda os
arquivos no storage e grava os hashes em app.dossie.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

from documentos.conteudo import contexto_permitido, validar_conteudo
from documentos.excel import montar_excel
from documentos.modelos import Arquivos, DadosDossie
from documentos.pdf import montar_pdf
from documentos.revisao import garantir_revisao

_PROIBIDOS_NO_NOME = re.compile(r'[\\/:*?"<>|]')


def _sha256(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def _codigo_verificacao(numero: str, conteudo: Mapping[str, Any]) -> str:
    """Código curto derivado do número e do texto emitido: confere se o texto mudou."""
    corpo = json.dumps(conteudo, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(f"{numero}|{corpo}".encode()).hexdigest()[:16].upper()
    return "-".join(digest[i : i + 4] for i in range(0, 16, 4))


def _nome_base(colaborador: str) -> str:
    limpo = _PROIBIDOS_NO_NOME.sub("", colaborador)
    return " ".join(limpo.split()) or "Colaborador"


def gerar_dossie(
    conteudo: Mapping[str, Any],
    perfil: str,
    dados: DadosDossie,
) -> Arquivos:
    validar_conteudo(conteudo)
    garantir_revisao(conteudo, dados.relato)

    visivel = contexto_permitido(perfil)
    texto: dict[str, Any] = dict(conteudo)
    if not visivel:
        texto.pop("contexto_acompanhamento", None)

    codigo = _codigo_verificacao(dados.numero, texto)
    pdf = montar_pdf(texto, dados, contexto_visivel=visivel, codigo_verificacao=codigo)
    xlsx = montar_excel(texto, dados, contexto_visivel=visivel, codigo_verificacao=codigo)

    base = _nome_base(dados.colaborador)
    return Arquivos(
        numero=dados.numero,
        codigo_verificacao=codigo,
        nome_pdf=f"Dossiê - {base}.pdf",
        pdf=pdf,
        sha256_pdf=_sha256(pdf),
        nome_xlsx=f"Dossiê - {base}.xlsx",
        xlsx=xlsx,
        sha256_xlsx=_sha256(xlsx),
    )
