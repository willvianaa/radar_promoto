"""Mascaramento de CPF em listas, tabelas, rankings e exports agregados (CLAUDE.md §3).

Formato: ``***.456.789-**``. Os 3 primeiros e os 2 últimos dígitos nunca aparecem; chave
provisória (sem CPF) não é mascarável e não pode virar "CPF" na tela.
"""

import re

import pytest

from regras import util
from tests.seguranca._apoio import cpfs_validos, dv_cpf, formatar

MASCARA = re.compile(r"^\*\*\*\.\d{3}\.\d{3}-\*\*$")
CPFS = cpfs_validos(200)


@pytest.mark.parametrize("entrada", ["digitos", "formatado"])
def test_mascara_esconde_inicio_e_verificadores(entrada):
    for cpf in CPFS:
        m = util.mascara_cpf(cpf if entrada == "digitos" else formatar(cpf))
        assert MASCARA.match(m), "máscara fora do formato ***.ddd.ddd-**"
        visiveis = re.sub(r"\D", "", m)
        assert visiveis == cpf[3:9], "a máscara deve expor só os dígitos 4 a 9"


@pytest.mark.parametrize("chave", ["N:FULANO DE TAL", "", None, "123", "1234567890", "123456789012"])
def test_chave_provisoria_ou_invalida_nao_vira_cpf(chave):
    assert util.mascara_cpf(chave) == ""


def test_cpf_numerico_de_planilha_mascara_igual_ao_texto():
    # Planilha entrega o CPF como número e perde zeros à esquerda: normaliza antes de mascarar.
    nove = "0" + CPFS[0][1:9]
    cpf = nove + dv_cpf(nove)
    assert util.mascara_cpf(util.normaliza_cpf(int(cpf))) == util.mascara_cpf(cpf)


def test_mascara_e_idempotente_sobre_a_propria_saida():
    # Mascarar de novo um valor já mascarado não pode "desmascarar" nem inventar dígitos.
    for cpf in CPFS[:20]:
        m = util.mascara_cpf(cpf)
        assert util.mascara_cpf(m) == ""
