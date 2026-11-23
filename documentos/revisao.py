"""Revisão final do texto antes de gerar o dossiê (CLAUDE.md §5).

Bloqueia termos proibidos e nomes de sistemas ou fornecedores. A revisão só
aponta onde está o problema (campo e termo); o trecho do texto não é repetido
na mensagem de erro, para não espalhar dado pessoal em logs.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

# Radicais dos termos proibidos (CLAUDE.md §5). Comparação sem acento e em minúsculas.
TERMOS_PROIBIDOS = (
    "detrat",
    "preguic",
    "irresponsav",
    "desonest",
    "relaps",
    "ma-fe",
    "mentiu",
    "mentir",
    "culpad",
    "comprovad",
    "fraud",
)

# Nomes de sistemas e fornecedores que não podem aparecer no corpo do dossiê.
# A lista é um piso: quem souber de outros nomes acrescenta aqui.
NOMES_DE_SISTEMAS = (
    "playwright",
    "fastapi",
    "postgres",
    "docker",
    "openpyxl",
    "reportlab",
    "pandas",
)


class RevisaoBloqueada(Exception):
    """A revisão encontrou termo proibido ou nome de sistema no texto."""

    def __init__(self, achados: list[Achado]):
        self.achados = achados
        resumo = "; ".join(f"{a.campo}: '{a.termo}'" for a in achados)
        super().__init__(f"Revisão bloqueou a emissão ({resumo})")


@dataclass(frozen=True)
class Achado:
    campo: str
    termo: str


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return sem_acento.lower()


_PADROES = [
    (termo, re.compile(r"(?<![a-z])" + re.escape(termo)))
    for termo in (*TERMOS_PROIBIDOS, *NOMES_DE_SISTEMAS)
]


def _textos(valor: Any, caminho: str) -> list[tuple[str, str]]:
    """Percorre o conteúdo e devolve pares (campo, texto)."""
    if isinstance(valor, str):
        return [(caminho, valor)]
    if isinstance(valor, Mapping):
        saida: list[tuple[str, str]] = []
        for chave, sub in valor.items():
            saida.extend(_textos(sub, f"{caminho}.{chave}" if caminho else str(chave)))
        return saida
    if isinstance(valor, list | tuple):
        saida = []
        for i, sub in enumerate(valor):
            saida.extend(_textos(sub, f"{caminho}[{i + 1}]"))
        return saida
    return []


def revisar(conteudo: Mapping[str, Any], relato: str | None = None) -> list[Achado]:
    """Lista os termos proibidos encontrados em todo o texto que vai ao documento."""
    campos = _textos(conteudo, "conteudo")
    if relato:
        campos.append(("relato", relato))
    achados: list[Achado] = []
    for campo, texto in campos:
        normalizado = _normalizar(texto)
        for termo, padrao in _PADROES:
            if padrao.search(normalizado):
                achados.append(Achado(campo=campo, termo=termo))
    return achados


def garantir_revisao(conteudo: Mapping[str, Any], relato: str | None = None) -> list[Achado]:
    """Levanta RevisaoBloqueada se houver achados. Sem achados, devolve lista vazia."""
    achados = revisar(conteudo, relato)
    if achados:
        raise RevisaoBloqueada(achados)
    return achados
