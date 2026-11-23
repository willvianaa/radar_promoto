"""Dados fictícios para os testes do dossiê. Nenhum nome, CPF ou número real."""

import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from documentos.modelos import DadosDossie, Grafico, ParametroAplicado, Serie, Tabela

FIXTURES = Path(__file__).parent / "fixtures"
FUSO = ZoneInfo("America/Sao_Paulo")


@pytest.fixture
def conteudo():
    return json.loads((FIXTURES / "conteudo_ficticio.json").read_text(encoding="utf-8"))


@pytest.fixture
def dados():
    return DadosDossie(
        numero="RP-2026-000001",
        emitido_em=datetime(2026, 10, 6, 10, 42, tzinfo=FUSO),
        emissor="RT Intelligence - Colaborador Ficticio Emissor",
        colaborador="Colaborador Ficticio Um",
        cpf="000.000.001-91",
        uf="XX",
        supervisor="Supervisor Ficticio Dois",
        periodo_ini=date(2026, 9, 1),
        periodo_fim=date(2026, 9, 30),
        parametro_versao=1,
        parametros=(
            ParametroAplicado("Tolerância de atraso (min)", "15", 1, date(2026, 1, 1)),
            ParametroAplicado("Corte de aderência do dossiê", "93%", 1, date(2026, 1, 1)),
        ),
        relato="Relato ficticio: saídas antes do horário e pesquisas não respondidas.",
        tabelas={
            "jornada": Tabela(
                colunas=("Data", "Dia", "Último check-out", "Antecipação (min)"),
                linhas=(
                    ("05/09/2026", "Sábado", "14:02", 78),
                    ("12/09/2026", "Sábado", "13:58", 82),
                    ("15/09/2026", "Terça", "14:21", 59),
                ),
                grafico=Grafico(
                    categorias=("05/09", "12/09", "15/09"),
                    series=(Serie("Antecipação (min)", (78, 82, 59)),),
                ),
            ),
            "pesquisas": Tabela(
                colunas=("Semana", "Programadas", "Respondidas", "Expiradas"),
                linhas=(
                    ("S36", 35, 33, 2),
                    ("S39", 14, 8, 6),
                ),
                grafico=Grafico(
                    categorias=("S36", "S39"),
                    series=(
                        Serie("Respondidas", (33, 8)),
                        Serie("Expiradas", (2, 6)),
                    ),
                ),
            ),
        },
    )
