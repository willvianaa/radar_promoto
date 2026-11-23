"""Regras do motor, uma a uma, com dados fictícios montados em memória."""

from datetime import date, timedelta

import pytest

from regras import motor
from regras.parametros import parametros_padrao, severidade
from regras.tipos import Aderencia, Atividade, Base, Colaborador, Falta, Foto, Humor, Posicao, Visita

CPF = "00000000191"
INI, FIM = date(2026, 9, 1), date(2026, 9, 25)
SEG = date(2026, 9, 14)  # segunda-feira, semana ISO 38


def pessoa(**kw):
    return Colaborador(cpf=CPF, nome="Joana Modelo Pereira", nome_norm="JOANA MODELO PEREIRA", uf="BA", **kw)


def visita(dia, cin=480, cout=1050, auto=False, pdv="BA / LOJA FICTICIA 01", tipo="loja"):
    return Visita(CPF, dia, pdv, tipo, cin, cout, auto)


def dias_uteis(n, a_partir=date(2026, 9, 1)):
    out, d = [], a_partir
    while len(out) < n:
        if d.weekday() < 5 and d != date(2026, 9, 7):
            out.append(d)
        d += timedelta(days=1)
    return out


def calc(base, **kw):
    (r,) = motor.calcular(base, kw.pop("params", None), INI, FIM, **kw)
    return r


def tipos(r):
    return {a.tipo: a.severidade for a in r.alertas}


# ---------------------------------------------------------------- limites e níveis

def test_limites_de_severidade():
    assert [severidade(v, [4, 7, 10]) for v in (3, 4, 6, 7, 9, 10, 20)] == [0, 1, 1, 2, 2, 3, 3]
    assert [severidade(v, [0, 1, 3]) for v in (0, 1, 2, 3)] == [0, 2, 2, 3]  # limite 0 desliga a faixa 1


@pytest.mark.parametrize("soma,n3,esperado", [(0, 0, "N"), (2, 0, "N"), (3, 0, "T"), (4, 0, "T"), (5, 0, "A"), (8, 1, "A"),
                                              (9, 0, "C"), (6, 2, "C"), (3, 2, "C")])
def test_niveis(soma, n3, esperado):
    assert motor.nivel_de(soma, n3, parametros_padrao()) == esperado


# ---------------------------------------------------------------- jornada

def test_atraso_com_tolerancia_e_escala_padrao():
    b = Base(colaboradores=[pessoa()], visitas=[visita(SEG, 495), visita(SEG + timedelta(1), 496)])
    r = calc(b)
    assert [x.atraso for x in r.dias] == [0, 16]  # 08:15 ainda está na tolerância; 08:16 não


def test_atraso_com_jornada_cadastrada_e_sem():
    v = [visita(SEG, 460)]  # 07:40
    sem = calc(Base(colaboradores=[pessoa()], visitas=v))
    com = calc(Base(colaboradores=[pessoa(jornada_ini=420, jornada_fim=990)], visitas=v))
    assert sem.dias[0].atraso == 0
    assert com.dias[0].atraso == 40  # 07:00 + 15 min de tolerância


def test_almoco_nao_e_visita_nem_dia_trabalhado():
    b = Base(colaboradores=[pessoa()], visitas=[
        visita(SEG, 480, 690), visita(SEG, 720, 780, pdv="BA / NÃO OPERACIONAL", tipo="nao_operacional"),
        visita(SEG + timedelta(1), 720, 780, pdv="BA / NÃO OPERACIONAL", tipo="nao_operacional")])
    r = calc(b)
    assert len(r.dias) == 1 and r.dias[0].lojas == 1


def test_almoco_no_inicio_do_dia_nao_vira_primeiro_checkin():
    b = Base(colaboradores=[pessoa()], visitas=[
        visita(SEG, 400, 410, pdv="BA / NÃO OPERACIONAL", tipo="nao_operacional"), visita(SEG, 480, 690)])
    assert calc(b).dias[0].checkin == 480


def test_checkout_automatico_conta_e_nao_e_saida():
    ds = dias_uteis(6)
    b = Base(colaboradores=[pessoa()], visitas=[visita(d, auto=True, cout=1050) for d in ds])
    r = calc(b, params={**parametros_padrao(), "saida_antecipada_ativa": True})
    assert tipos(r) == {"auto": 1}  # 6 dias com check-out automático: [5,8,10] → 1, e nenhuma saída antecipada
    assert all(x.saida == 0 and x.checkout is None for x in r.dias)


def test_saida_antecipada_so_quando_ativa_e_com_checkout_manual():
    ds = dias_uteis(4)
    v = [visita(d, 480, 960) for d in ds]  # saiu 16:00, jornada até 17:30
    off = calc(Base(colaboradores=[pessoa()], visitas=v))
    assert all(x.saida == 0 for x in off.dias)  # saida_antecipada_ativa = false
    on = calc(Base(colaboradores=[pessoa()], visitas=v), params={**parametros_padrao(), "saida_antecipada_ativa": True})
    assert [x.saida for x in on.dias] == [90] * 4
    assert tipos(on) == {"jor": 1}  # 4 saídas → severidade 1


def test_feriado_nacional_e_estadual_nao_geram_atraso():
    v = [visita(date(2026, 9, 7), 600), visita(date(2026, 9, 16), 600), visita(SEG, 600)]
    b = Base(colaboradores=[pessoa()], visitas=v, feriados={(date(2026, 9, 7), None), (date(2026, 9, 16), "BA")})
    assert [x.atraso for x in calc(b).dias] == [0, 120, 0]  # 07/09 (nacional), 14/09 (normal), 16/09 (BA)
    # feriado de outra UF não vale para a pessoa
    b2 = Base(colaboradores=[pessoa()], visitas=v, feriados={(date(2026, 9, 16), "CE")})
    assert [x.atraso for x in calc(b2).dias][2] == 120


# ---------------------------------------------------------------- pesquisas

def pesquisas(n, expiradas, dia=SEG, pdv="BA / LOJA FICTICIA 01"):
    return [Atividade(f"P{i}", CPF, dia + timedelta(days=i % 4), pdv, "MARCA A", "Preço", "E" if i < expiradas else "R")
            for i in range(n)]


def test_pesquisas_expiradas_exigem_minimo_de_20():
    abaixo = Base(colaboradores=[pessoa()], atividades=pesquisas(19, 19))
    assert "pesq" not in tipos(calc(abaixo))
    no_minimo = Base(colaboradores=[pessoa()], atividades=pesquisas(20, 9))  # 45% → severidade 3
    assert tipos(calc(no_minimo))["pesq"] == 3
    faixa = Base(colaboradores=[pessoa()], atividades=pesquisas(20, 4))  # 20% → 1
    assert tipos(calc(faixa))["pesq"] == 1


def test_dia_sem_atividades_exige_visita_e_dia_fora_de_feriado():
    ps = [Atividade(f"P{i}", CPF, d, "BA / L", "M", "T", "E") for i, d in enumerate([SEG, SEG + timedelta(1), SEG + timedelta(2), SEG + timedelta(3)])]
    vs = [visita(SEG), visita(SEG + timedelta(1)), visita(SEG + timedelta(3))]  # dia 16 sem visita
    b = Base(colaboradores=[pessoa()], atividades=ps, visitas=vs, feriados={(SEG + timedelta(3), None)})
    # 14 e 15 contam; 16 não tem visita; 17 é feriado → 2 dias → severidade 2
    assert tipos(calc(b)).get("exec") == 2


# ---------------------------------------------------------------- aderência e carga

def ader(sem, ct, rz, marca="MARCA A", fechada=True, loja="BA / LOJA FICTICIA 01"):
    return Aderencia(CPF, loja, marca, "BA", sem, ct, rz, fechada)


def semanas(n=3):
    return [date(2026, 8, 31) + timedelta(weeks=i) for i in range(n)]


def test_aderencia_teto_por_linha_o_excesso_nao_compensa_o_deficit():
    s = semanas(2)
    # semana 1: 10 de 10 e 14 de 4 (excesso); semana 2: 6 de 10. Sem teto: 30/24; com teto por linha: 10+4+6 = 20/24
    b = Base(colaboradores=[pessoa()], aderencia=[ader(s[0], 10, 10), ader(s[0], 4, 14, marca="MARCA B"), ader(s[1], 10, 6)])
    r = calc(b)
    assert r.aderencia_pct == pytest.approx(20 / 24)
    assert r.dimensoes["aderencia"] == 83
    (a,) = [x for x in r.alertas if x.tipo == "ader"]
    assert a.severidade == 2  # abaixo de 85% (severidade 2) (grupo MARCA A: 16/20 = 80%)


def test_semana_em_andamento_fica_fora_dos_alertas():
    s = semanas(2)
    b = Base(colaboradores=[pessoa()], aderencia=[ader(s[0], 10, 10), ader(s[1], 10, 0, fechada=False)])
    r = calc(b)
    assert "ader" not in tipos(r) and r.aderencia_pct == 1.0


def test_so_semana_em_andamento_nao_cria_colaborador():
    b = Base(colaboradores=[pessoa()], aderencia=[ader(semanas(1)[0], 10, 0, fechada=False)])
    assert motor.calcular(b, None, INI, FIM) == []


def test_aderencia_sem_colaborador_e_ignorada():
    sem = Aderencia(None, "BA / L", "M", "BA", semanas(1)[0], 10, 0, True)
    assert motor.calcular(Base(colaboradores=[pessoa()], aderencia=[sem]), None, INI, FIM) == []


def test_metas_1_e_2_e_severidade_pelas_pendentes():
    s = semanas(1)[0]
    assert "abaixo da meta de 93%" in next(a for a in meta2.alertas if a.tipo == "ader").detalhe
    meta2 = calc(Base(colaboradores=[pessoa()], aderencia=[ader(s, 100, 90)]))  # 90%: abaixo de 93%; 10 pendentes
    assert tipos(meta2)["ader"] == 3
    ok = calc(Base(colaboradores=[pessoa()], aderencia=[ader(s, 100, 93)]))
    assert "ader" not in tipos(ok)
    meta1 = calc(Base(colaboradores=[pessoa()], aderencia=[ader(s, 10, 8)]))  # 80%: abaixo de 85% (severidade 2); 2 pendentes
    assert tipos(meta1)["ader"] == 2


def sobrecarga_base(media, rz_ultima, humor=()):
    s = semanas(3)
    return Base(colaboradores=[pessoa()],
                aderencia=[ader(s[0], media, media), ader(s[1], media, media), ader(s[2], media, rz_ultima)],
                humor=list(humor))


def test_sobrecarga_exige_carga_e_queda():
    # 44 visitas/semana, 100% → 88% (12 p.p.) → indício
    r = calc(sobrecarga_base(44, 39))
    assert tipos(r) == {"sobre": 2}
    assert r.carga_media == 44 and r.queda_ader_pp == pytest.approx(11.36, abs=0.01)
    # 43 por semana: abaixo do limite
    assert "sobre" not in tipos(calc(sobrecarga_base(43, 38)))
    # queda de 4,5 p.p. (< 5): sem indício
    assert "sobre" not in tipos(calc(sobrecarga_base(200, 191)))
    # queda de exatamente 5 p.p. com carga alta
    assert "sobre" in tipos(calc(sobrecarga_base(200, 190)))


def test_sobrecarga_precisa_de_duas_semanas_fechadas():
    s = semanas(1)[0]
    assert "sobre" not in tipos(calc(Base(colaboradores=[pessoa()], aderencia=[ader(s, 60, 10)])))


def humor_negativo_seguido(n=5, extra_positivos=0):
    ds = dias_uteis(n + extra_positivos)
    return [Humor(CPF, d, "Cansado" if i < n else "Feliz", i < n) for i, d in enumerate(ds)]


def test_humor_reforca_sobrecarga_com_severidade_3():
    r = calc(sobrecarga_base(44, 39, humor_negativo_seguido()))
    assert tipos(r) == {"sobre": 3}
    assert "Humor negativo em 100% dos dias" in r.alertas[0].detalhe


def test_humor_sozinho_soma_um_ponto():
    r = calc(Base(colaboradores=[pessoa()], humor=humor_negativo_seguido()))
    assert tipos(r) == {"humor": 1}
    assert r.score == 1 and r.nivel == "N"


def test_humor_soma_pontos_e_o_risco_e_soma_vezes_10():
    """Com humor negativo recorrente: +2 pontos (sobrecarga por humor + queda de desempenho); risco = soma × 10."""
    ds = dias_uteis(10)
    vis = [visita(d, 520) for d in ds[:5]] + [visita(d) for d in ds[5:]]  # 5 atrasos → severidade 1
    ps = pesquisas(24, 8)  # 33% expiradas → 2
    base = Base(colaboradores=[pessoa()], visitas=vis, atividades=ps)
    com_humor = Base(colaboradores=[pessoa()], visitas=vis, atividades=ps,
                     humor=[Humor(CPF, d, "Sobrecarregado", True) for d in ds])
    a, b = calc(base), calc(com_humor)
    assert tipos(b) == {**tipos(a), "sobre": 2}
    assert b.score == a.score + 2
    assert b.dimensoes["humor"] == 0 and a.dimensoes["humor"] is None
    assert b.risco == b.score * 10 and a.risco == a.score * 10  # as dimensões não entram na conta


def test_sobrecarga_vale_3_quando_carga_e_humor_aparecem_juntos():
    r = calc(sobrecarga_base(44, 39, humor_negativo_seguido()))
    assert tipos(r) == {"sobre": 3} and r.score == 3 and r.nivel == "T"
    so_carga = calc(sobrecarga_base(44, 39))
    assert tipos(so_carga) == {"sobre": 2} and so_carga.score == 2


def test_doente_fica_em_campo_estruturado_e_fora_do_texto():
    ds = dias_uteis(6)
    b = Base(colaboradores=[pessoa()], humor=[Humor(CPF, d, "Doente", True) for d in ds])
    a = calc(b).alertas[0]
    assert a.dias_doente == 6  # R10 (LGPD): contagem estruturada, que a API filtra por perfil
    assert "doente" not in f"{a.titulo} {a.detalhe}".lower()


def test_humor_so_conta_com_5_dias_de_registro():
    ds = dias_uteis(4)
    b = Base(colaboradores=[pessoa()], humor=[Humor(CPF, d, "Triste", True) for d in ds])
    assert calc(b).alertas == []


# ---------------------------------------------------------------- fotos, rota, faltas

def foto(dia, sha, hora=540, lat=None, plat=None, pdv="BA / LOJA FICTICIA 01"):
    return Foto(CPF, dia, hora, pdv, None, sha, lat=lat, lon=-38.5 if lat is not None else None,
                pdv_lat=plat, pdv_lon=-38.5 if plat is not None else None)


def test_fotos_repetida_distancia_e_horario():
    ds = dias_uteis(3)
    vs = [visita(d, 480, 690) for d in ds]
    fs = [foto(ds[0], "a" * 64), foto(ds[1], "a" * 64),                        # mesma imagem em duas visitas
          foto(ds[2], "b" * 64, lat=-12.8942, plat=-12.9),                       # ~645 m da loja
          foto(ds[0], "c" * 64, hora=1000),                                      # fora do horário da visita
          foto(ds[1], "d" * 64, hora=540)]                                       # limpa
    r = calc(Base(colaboradores=[pessoa()], visitas=vs, fotos=fs))
    (a,) = [x for x in r.alertas if x.tipo == "foto"]
    assert a.severidade == 3 and a.titulo == "Fotos com indício"
    assert a.detalhe.startswith("4 fotos de 5 analisadas")
    for trecho in ("imagem repetida", "captura a x m da loja", "fora do horário da visita"):
        assert trecho in a.detalhe


def test_foto_na_mesma_visita_com_hash_repetido_nao_e_indicio():
    d = dias_uteis(1)[0]
    r = calc(Base(colaboradores=[pessoa()], visitas=[visita(d, 480, 690)], fotos=[foto(d, "a" * 64), foto(d, "a" * 64, hora=550)]))
    assert "foto" not in tipos(r)


def test_fuga_de_rota():
    ds = dias_uteis(4)
    po = [Posicao(CPF, d, 600, "BA / L", 250.0) for d in ds] + [Posicao(CPF, ds[0], 610, "BA / L", 150.0)]
    r = calc(Base(colaboradores=[pessoa()], posicoes=po))
    (a,) = r.alertas
    assert a.tipo == "rota" and a.severidade == 2 and "4 posições fora da cerca de 200 m em 4 dias" in a.detalhe


def test_faltas_injustificadas_e_atestado_sem_alerta():
    d = dias_uteis(3)
    r = calc(Base(colaboradores=[pessoa()], faltas=[Falta(CPF, d[0], "A"), Falta(CPF, d[1], "J", "motivo fictício")]))
    assert r.alertas == [] and r.dimensoes["presenca"] == 94
    r2 = calc(Base(colaboradores=[pessoa()], faltas=[Falta(CPF, x, "I") for x in d]))
    assert tipos(r2) == {"falta": 3} and r2.dimensoes["presenca"] == 25


def test_motivo_de_falta_nunca_vai_para_o_texto():
    d = dias_uteis(1)[0]
    r = calc(Base(colaboradores=[pessoa()], faltas=[Falta(CPF, d, "I", "MOTIVO SECRETO")]))
    assert all("SECRETO" not in a.detalhe + a.titulo for a in r.alertas)


# ---------------------------------------------------------------- risco e determinismo

def test_risco_limitado_a_100():
    ds = dias_uteis(12)
    b = Base(colaboradores=[pessoa()], visitas=[visita(d, 540, auto=True) for d in ds],
             faltas=[Falta(CPF, d, "I") for d in ds[:5]], atividades=pesquisas(24, 12))
    r = calc(b)
    assert r.nivel == "C" and r.risco == 100


def test_determinismo_e_parametros_nao_mudam():
    ds = dias_uteis(8)
    b = Base(colaboradores=[pessoa()], visitas=[visita(d, 520) for d in ds], humor=humor_negativo_seguido())
    p = parametros_padrao()
    antes = parametros_padrao()
    r1, r2 = calc(b, params=p), calc(b, params=p)
    assert r1 == r2 and p == antes


def test_parametros_versionados_mudam_o_resultado():
    ds = dias_uteis(5)
    b = Base(colaboradores=[pessoa()], visitas=[visita(d, 520) for d in ds])
    p2 = parametros_padrao()
    p2["limites"]["atraso"] = [2, 4, 6]
    assert tipos(calc(b)) == {"jor": 1} and tipos(calc(b, params=p2)) == {"jor": 2}


def test_periodo_filtra_registros():
    b = Base(colaboradores=[pessoa()], visitas=[visita(date(2026, 8, 20), 600), visita(SEG, 600)])
    assert len(calc(b).dias) == 1


def test_sem_cadastro_usa_chave_provisoria_como_nome():
    v = Visita("N:FULANO SEM CADASTRO", SEG, "BA / L", "loja", 480, 1050, False)
    (r,) = motor.calcular(Base(visitas=[v]), None, INI, FIM)
    assert r.cpf_pendente and r.nome == "FULANO SEM CADASTRO"
