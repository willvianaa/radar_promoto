"""Validação da estrutura do conteúdo pronto (api/openapi.yaml, ConteudoDossie) e
regra de visibilidade da seção de contexto de acompanhamento.

Não altera texto: só confere forma e permissão.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

CONCLUSOES = {
    "procede": "Procede",
    "procede_parcialmente": "Procede parcialmente",
    "nao_procede": "Não procede",
    "sem_dados": "Sem dados",
}
MAX_BLOCOS = 5
ABERTURA_FINAL = "Sendo assim,"

# Perfis que recebem a seção "Contexto de acompanhamento" (docs/05-matriz-permissoes.md, §5.2).
# Compliance e Supervisor aparecem como ✔ na matriz, mas o acesso ao humor individual
# depende de Q-08 (base legal, CLAUDE.md §2.1), por isso ficam de fora até a decisão.
PERFIS_COM_CONTEXTO = frozenset({"rh", "gerencia_regional"})


class ConteudoInvalido(ValueError):
    """O conteúdo não segue o contrato ConteudoDossie."""


def contexto_permitido(perfil: str) -> bool:
    return perfil in PERFIS_COM_CONTEXTO


def validar_conteudo(conteudo: Mapping[str, Any]) -> None:
    erros: list[str] = []

    final = conteudo.get("consideracoes_finais")
    if not isinstance(final, str) or not final.lstrip().startswith(ABERTURA_FINAL):
        erros.append("consideracoes_finais deve começar com 'Sendo assim,'")

    for campo in ("intro", "objetivos", "impacto"):
        valor = conteudo.get(campo, "")
        if valor is not None and not isinstance(valor, str):
            erros.append(f"{campo} deve ser texto")

    blocos = conteudo.get("blocos", [])
    if not isinstance(blocos, list):
        erros.append("blocos deve ser uma lista")
        blocos = []
    if len(blocos) > MAX_BLOCOS:
        erros.append(f"no máximo {MAX_BLOCOS} blocos de relatos")
    chaves: set[str] = set()
    for i, bloco in enumerate(blocos, start=1):
        if not isinstance(bloco, Mapping):
            erros.append(f"bloco {i} inválido")
            continue
        for campo in ("chave", "titulo", "texto"):
            if not isinstance(bloco.get(campo), str) or not bloco[campo].strip():
                erros.append(f"bloco {i}: {campo} obrigatório")
        chave = bloco.get("chave")
        if isinstance(chave, str):
            if chave in chaves:
                erros.append(f"bloco {i}: chave '{chave}' repetida")
            chaves.add(chave)
        conclusao = bloco.get("conclusao")
        if conclusao is not None and conclusao not in CONCLUSOES:
            erros.append(f"bloco {i}: conclusão inválida")

    if erros:
        raise ConteudoInvalido("; ".join(erros))


def rotulo_conclusao(chave: str | None) -> str | None:
    return CONCLUSOES.get(chave) if chave else None
