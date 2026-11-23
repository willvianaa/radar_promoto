"""Nada sensível sai do motor em texto livre nem em log (CLAUDE.md §2, §2.1 e §4.4).

- Título e detalhe de alerta são exibidos a vários perfis (aba Alertas, Visão Geral): não trazem
  CPF, motivo de falta nem a opção de humor "Doente" (dado de saúde, art. 11 da LGPD).
- Colaborador com CPF e sem cadastro aparece pelo CPF **mascarado**, nunca completo.
- Logs da transformação, do motor e do agendador não registram CPF, humor individual nem motivo
  de falta.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

import pytest

from ingestor import agendador
from regras import motor
from regras import transformacao as t
from regras.parametros import parametros_padrao
from regras.tipos import Base, Colaborador, Falta, Humor, Visita
from tests.fixtures import cenario as c
from tests.seguranca._apoio import cpfs_validos, formatar, vazamentos

CPF_A, CPF_B, CPF_C = cpfs_validos(3, semente=11)
MOTIVO = "motivo sigiloso de teste"
INI, FIM = date(2026, 9, 1), date(2026, 9, 30)


def _dias_uteis(n: int) -> list[date]:
    out, d = [], date(2026, 9, 1)
    while len(out) < n:
        if d.weekday() < 5 and d != date(2026, 9, 7):
            out.append(d)
        d += timedelta(days=1)
    return out


def _base_sensivel() -> Base:
    """A: atrasos, humor "Doente" e faltas com motivo (vira "Possível sobrecarga").
    B: sem cadastro. C: só humor "Doente" recorrente, sem queda de desempenho (vira "Humor negativo")."""
    dias = _dias_uteis(12)
    a = Colaborador(cpf=CPF_A, nome="Ana Exemplo Ficticia", nome_norm="ANA EXEMPLO FICTICIA", uf="BA")
    visitas = [Visita(CPF_A, d, "BA / LOJA FICTICIA 01", "loja", 540, 1050, False) for d in dias]
    visitas += [Visita(CPF_B, d, "BA / LOJA FICTICIA 02", "loja", 540, 1050, False) for d in dias]
    c_ = Colaborador(cpf=CPF_C, nome="Caio Exemplo Ficticio", nome_norm="CAIO EXEMPLO FICTICIO", uf="BA")
    visitas += [Visita(CPF_C, d, "BA / LOJA FICTICIA 03", "loja", 480, 1050, False) for d in dias]
    humor = [Humor(cpf, d, "Doente", True) for cpf in (CPF_A, CPF_C) for d in dias[:8]]
    faltas = [Falta(CPF_A, date(2026, 9, 29), "I", MOTIVO), Falta(CPF_A, date(2026, 9, 30), "I", MOTIVO)]
    return Base(colaboradores=[a, c_], visitas=visitas, humor=humor, faltas=faltas)


@pytest.fixture(scope="module")
def resultados():
    return motor.calcular(_base_sensivel(), parametros_padrao(), INI, FIM)


def _textos_de_alerta(resultados) -> list[str]:
    return [f"{a.titulo} {a.detalhe}" for r in resultados for a in r.alertas]


def test_cenario_gera_alertas(resultados):
    # Garante que os testes abaixo olham para textos de verdade, não para lista vazia.
    tipos = {a.tipo for r in resultados for a in r.alertas}
    assert {"jor", "falta"} <= tipos
    assert {"humor", "sobre"} <= tipos


def test_alerta_nao_traz_cpf(resultados):
    for texto in _textos_de_alerta(resultados):
        assert not vazamentos(texto, [CPF_A, CPF_B, CPF_C])


def test_alerta_nao_traz_motivo_de_falta(resultados):
    for texto in _textos_de_alerta(resultados):
        assert MOTIVO not in texto.lower()


def test_alerta_nao_traz_opcao_doente(resultados):
    # R10: "Doente" (dado de saúde) fica fora do texto livre; a contagem vai em campo
    # estruturado (Alerta.dias_doente), que a API só entrega a perfis autorizados.
    for texto in _textos_de_alerta(resultados):
        assert "doente" not in texto.lower()
    humor = [a for r in resultados if r.cpf == CPF_C for a in r.alertas if a.tipo == "humor"]
    assert humor and humor[0].dias_doente == 8


def test_sem_cadastro_aparece_mascarado(resultados):
    sem_cad = next(r for r in resultados if r.cpf == CPF_B)
    assert not vazamentos(sem_cad.nome, [CPF_B])
    assert sem_cad.nome.startswith("***.")


def test_chave_provisoria_nao_expoe_prefixo_interno():
    colab = t.transforma_colaboradores(c.cadastro())
    cad = t.Cadastro(colab)
    b = Base(colaboradores=colab, feriados=set(c.FERIADOS))
    b.visitas, _ = t.transforma_operacao(c.operacao(), cad)
    (dora,) = [r for r in motor.calcular(b, parametros_padrao(), c.INI, c.FIM) if r.cpf == c.DORA]
    assert not dora.nome.startswith("N:")


def test_logs_do_pipeline_sem_dado_sensivel(caplog):
    """Transformação + motor em DEBUG: nenhum CPF, humor individual ou motivo de falta no log."""
    caplog.set_level(logging.DEBUG)
    cpfs_cenario = [c.JOANA, c.PEDRO, c.CAIO]
    p = parametros_padrao()
    colab = t.transforma_colaboradores(c.cadastro())
    cad = t.Cadastro(colab)
    b = Base(colaboradores=colab, feriados=set(c.FERIADOS))
    b.visitas, _ = t.transforma_operacao(c.operacao(), cad)
    b.atividades = t.transforma_atividades(c.atividades(), cad)
    b.humor = t.transforma_humor(c.humor(), cad, p["humor_negativo"])
    b.faltas = t.transforma_faltas(c.faltas(), cad)
    b.aderencia = t.transforma_aderencia(c.aderencia(), cad, c.HOJE)
    b.pdoh = t.transforma_pdoh(c.pdoh(), cad, c.INI, c.FIM)
    b.fotos = t.transforma_fotos(c.fotos(), cad)
    motor.calcular(b, p, c.INI, c.FIM)
    motor.calcular(_base_sensivel(), p, INI, FIM)

    texto = "\n".join(rec.getMessage() for rec in caplog.records)
    # Os fictícios do cenário (000.000.00x) também contam: o teste é sobre o formato, não o valor.
    assert not vazamentos(texto, cpfs_cenario + [CPF_A, CPF_B, CPF_C])
    baixo = texto.lower()
    assert MOTIVO not in baixo and "motivo fictício" not in baixo
    for opcao in ("doente", "triste", "cansado", "sobrecarregado"):
        assert opcao not in baixo


def test_log_do_agendador_sem_dado_sensivel(caplog):
    caplog.set_level(logging.DEBUG)
    agendador.executar_ingestor()
    texto = "\n".join(rec.getMessage() for rec in caplog.records)
    assert not vazamentos(texto, [CPF_A, CPF_B])
    assert formatar(CPF_A) not in texto
