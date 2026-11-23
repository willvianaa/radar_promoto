"""Apoio dos testes de segurança.

Os CPFs "válidos" usados aqui são gerados em tempo de teste (semente fixa), nunca escritos no
arquivo: assim o próprio teste não vira achado da varredura de CPF (CLAUDE.md §2) e nenhum valor
fica no repositório. Os fictícios do cenário seguem a convenção ``000.000.00x-xx``.
"""

from __future__ import annotations

import random
import re


def dv_cpf(nove: str) -> str:
    """Dois dígitos verificadores de um CPF a partir dos 9 primeiros dígitos."""
    nums = [int(c) for c in nove]
    for pos in (9, 10):
        soma = sum(nums[i] * (pos + 1 - i) for i in range(pos))
        nums.append((soma * 10) % 11 % 10)
    return "".join(str(n) for n in nums[9:])


def cpfs_validos(n: int, semente: int = 2026) -> list[str]:
    """``n`` CPFs com dígitos verificadores válidos, só dígitos, gerados de forma reproduzível."""
    rng = random.Random(semente)  # nosec B311 - dado de teste, não é uso criptográfico
    saida: list[str] = []
    while len(saida) < n:
        nove = "".join(str(rng.randint(0, 9)) for _ in range(9))
        if len(set(nove)) == 1 or nove.startswith("00000000"):
            continue
        saida.append(nove + dv_cpf(nove))
    return saida


def formatar(cpf: str) -> str:
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def vazamentos(texto: str, cpfs: list[str]) -> list[str]:
    """Quais formas completas dos ``cpfs`` aparecem em ``texto`` (só dígitos ou formatado).

    Devolve apenas o tipo do vazamento, nunca o valor, para que uma falha de teste não
    reproduza o CPF no log do CI.
    """
    achados: list[str] = []
    so_digitos = re.sub(r"\D", "", texto)
    for i, cpf in enumerate(cpfs):
        if formatar(cpf) in texto:
            achados.append(f"cpf[{i}] formatado")
        elif cpf in texto:
            achados.append(f"cpf[{i}] só dígitos")
        elif cpf in so_digitos and len(cpf) == 11:
            achados.append(f"cpf[{i}] com separadores")
    return achados
