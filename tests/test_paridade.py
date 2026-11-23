"""Paridade com o protótipo, num cenário fictício calculado à mão (tests/fixtures/cenario.py).

Os números esperados foram calculados a mão com as fórmulas do protótipo (``radar_v2/engine.js`` +
patches da v3), uma conta por linha de comentário. O protótipo não foi executado (não há node
neste ambiente): a conta à mão é a referência.

Única diferença deliberada: humor nunca soma pontos (CLAUDE.md §4.4). O teste
``test_com_humor_penalizando_reproduz_o_prototipo`` liga o comportamento antigo e confere os
valores que o protótipo daria.
"""

from datetime import date

import pytest

from regras import motor
from regras import transformacao as t
from regras.parametros import parametros_padrao
from regras.tipos import Base
from tests.fixtures import cenario as c


@pytest.fixture(scope="module")
def base() -> Base:
    colab = t.transforma_colaboradores(c.cadastro())
    cad = t.Cadastro(colab)
    b = Base(colaboradores=colab, feriados=set(c.FERIADOS))
    b.visitas, _ = t.transforma_operacao(c.operacao(), cad)
    b.atividades = t.transforma_atividades(c.atividades(), cad)
    b.humor = t.transforma_humor(c.humor(), cad, parametros_padrao()["humor_negativo"])
    b.faltas = t.transforma_faltas(c.faltas(), cad)
    b.aderencia = t.transforma_aderencia(c.aderencia(), cad, c.HOJE)
    b.pdoh = t.transforma_pdoh(c.pdoh(), cad, c.INI, c.FIM)
    b.fotos = t.transforma_fotos(c.fotos(), cad)
    return b


@pytest.fixture(scope="module")
def r(base):
    return {x.cpf: x for x in motor.calcular(base, parametros_padrao(), c.INI, c.FIM)}


def tipos(res):
    return {a.tipo: a.severidade for a in res.alertas}


def test_quem_entra_e_ordem(r):
    assert set(r) == {c.JOANA, c.PEDRO, c.CAIO, c.DORA}
    res = motor.calcular(Base(), None, c.INI, c.FIM)
    assert res == []


def test_joana(r):
    j = r[c.JOANA]
    # jornada: 9 dias trabalhados (14,15,16,17,18,21,22,23,24); o dia 25 só tem almoço.
    assert len(j.dias) == 9
    # atrasos: 14,15,17,18 (08:30 > 08:15). 16 é feriado BA (sem atraso), 21 abre com reunião 08:00,
    # 22 chega 08:15 (limite da tolerância, não é atraso), 23 e 24 às 08:00.
    assert [x.data.day for x in j.dias if x.atraso] == [14, 15, 17, 18]
    assert [x.data.day for x in j.dias if x.auto] == [23, 24]
    # alertas e severidades:
    #  jor  4 atrasos        → [4,7,10] → 1
    #  auto 2 dias           → [5,8,10] → 0 (sem alerta)
    #  pesq 5/25 = 20%       → [20,30,45], 25 ≥ 20 programadas → 1
    #  exec só 24/09 (16 é feriado) → 1 dia → [0,2,4] → 0
    #  ader grupo MARCA A: 26 de 30 (86,7%) → abaixo da Meta 2, 4 pendentes → max(1, 2) = 2
    #       MARCA B: 6 realizadas viram 4 pelo teto da linha → 12/12 ok
    #  foto 1 de 10 fora do horário → [0,1,3] → 2
    #  sobre: humor 14,15,16 negativos (seq 3 ≥ 3) com atrasos ≥ 4 → sev 2, sem carga alta → 0 ponto
    assert tipos(j) == {"jor": 1, "pesq": 1, "ader": 2, "foto": 2, "sobre": 2}
    assert j.score == 6  # 1 + 1 + 2 + 2 (sobrecarga por humor não pontua)
    assert j.nivel == "A"  # 5 ≤ 6 < 9, nenhuma severidade 3
    # dimensões: ader 38/42 = 90,5 → 90 · pesq 100-20×4 = 20 · pont 100-4/9×200 = 11
    #            reg 100-2/9×200 = 56 · fotos 100-1/10×500 = 50 · presença 100-1×6 = 94 · humor 100-33,3 = 67
    assert j.dimensoes == {"aderencia": 90, "pesquisas": 20, "pontualidade": 11, "registro_jornada": 56,
                           "fotos": 50, "presenca": 94, "humor": 67}
    # risco = 6×9 + (100 - (90+20+11+56+50+94)/6) × 0,25 = 54 + 11,625 = 65,6 → 66
    assert j.risco == 66
    # semanas fechadas 36, 37, 38: contratado 14/semana; aderência 92,9% → 78,6% (queda 14,3 p.p.)
    assert j.carga_media == 14
    assert j.queda_ader_pp == pytest.approx(14.2857, abs=1e-3)
    assert j.sobrecarga is True
    # leitura cruzada: atrasos 14 e 15 caíram em dias de humor negativo; semana 38 concentra 3 das 5 expiradas
    assert j.cruzada == [
        "2 dos 4 atrasos ocorreram em dias com humor negativo",
        "a semana 38 concentra 3 das 5 pesquisas expiradas e teve 3 dias com humor negativo",
    ]
    sobre = next(a for a in j.alertas if a.tipo == "sobre")
    assert sobre.data_ref == date(2026, 9, 16)
    assert "queda de desempenho e 2 lojas atendidas" in sobre.detalhe  # reunião e almoço não contam como loja


def test_pedro_jornada_cadastrada_e_sobrecarga(r):
    p = r[c.PEDRO]
    # jornada 07:00: tolerância até 07:15; 21,22,23 chegam 07:40 → 3 atrasos (< 4: sem alerta)
    assert [x.data.day for x in p.dias if x.atraso] == [21, 22, 23]
    assert all(x.atraso == 40 for x in p.dias if x.atraso)
    # carga: 46 visitas/semana nas semanas 36-38 (a 39, em andamento, fica fora); 100% → 87% = 13 p.p.
    assert p.carga_media == 46
    assert p.queda_ader_pp == pytest.approx(13.0435, abs=1e-3)
    # humor: 5 dos 8 dias negativos em sequência (62,5% ≥ 40) reforça → severidade 3, mas só a carga pontua (2)
    assert tipos(p) == {"sobre": 3}
    assert p.score == 2 and p.nivel == "N"
    det = p.alertas[0].detalhe
    assert det == ("Média de 46 visitas contratadas por semana (até 1 loja) e aderência de 100% para 87% nas semanas fechadas. "
                   "Humor negativo em 63% dos dias (maior sequência: 5 dias). "
                   "PDOH: 60% produtivo, 10% ócio e 10% sem registro.")
    assert p.cruzada == ["3 dos 3 atrasos ocorreram em dias com humor negativo"]
    # dims: ader 130/138 = 94 · pesq 100 · pont 100-3/8×200 = 25 · reg 100 · presença 100 (sem fotos)
    assert p.dimensoes["aderencia"] == 94 and p.dimensoes["pontualidade"] == 25 and p.dimensoes["fotos"] is None
    # risco = 2×9 + (100 - (94+100+25+100+100)/5) × 0,25 = 18 + 4,05 = 22,05 → 22
    assert p.risco == 22


def test_caio_critico(r):
    k = r[c.CAIO]
    # 10 atrasos (→ 3), 10 check-outs automáticos (→ 3), 1 falta injustificada (→ 2): soma 8, duas severidades 3
    assert tipos(k) == {"jor": 3, "auto": 3, "falta": 2}
    assert k.score == 8 and k.nivel == "C"
    # pont 0 · reg 0 · presença 75 → risco = 8×9 + (100-25)×0,25 = 72 + 18,75 = 90,75 → 91
    assert k.risco == 91


def test_dora_chave_provisoria(r):
    d = r[c.DORA]
    assert d.cpf_pendente and d.nome == "DORA SEM CADASTRO"
    assert d.alertas == [] and d.nivel == "N" and d.risco == 0


def test_ordem_do_resultado(base):
    res = motor.calcular(base, parametros_padrao(), c.INI, c.FIM)
    assert [x.cpf for x in res] == [c.CAIO, c.JOANA, c.PEDRO, c.DORA]


def test_com_humor_penalizando_reproduz_o_prototipo(base):
    """Com ``humor_penaliza=True`` o motor soma a severidade cheia de ``sobre``, como o protótipo."""
    r = {x.cpf: x for x in motor.calcular(base, parametros_padrao(), c.INI, c.FIM, humor_penaliza=True)}
    # Joana: 1+1+2+2+2 = 8 → A · risco = 72 + 11,625 = 83,6 → 84
    assert (r[c.JOANA].score, r[c.JOANA].nivel, r[c.JOANA].risco) == (8, "A", 84)
    # Pedro: sobre severidade 3 → soma 3, uma sev 3 → Atenção · risco = 27 + 4,05 = 31
    assert (r[c.PEDRO].score, r[c.PEDRO].nivel, r[c.PEDRO].risco) == (3, "T", 31)
    assert (r[c.CAIO].nivel, r[c.CAIO].risco) == ("C", 91)  # sem humor: igual
