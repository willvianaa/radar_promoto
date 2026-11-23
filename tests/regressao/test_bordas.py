"""Casos de borda ponta a ponta (linhas cruas → transformação → motor). Dados 100% fictícios.

Testes ``xfail(strict=True)`` documentam defeitos achados pela QA (docs/qa/achados.md): quando a
área dona corrigir, o teste passa a falhar como "XPASS" e o marcador deve ser removido.
"""

from datetime import date

import pytest

from regras import motor, transformacao as t, util
from regras.parametros import parametros_padrao
from regras.tipos import Base, Colaborador, Visita

INI, FIM = date(2026, 9, 1), date(2026, 9, 25)
CPF = "00000000191"
NOME = "Joana Modelo Pereira"


def cadastro():
    return [Colaborador(cpf=CPF, nome=NOME, nome_norm=util.norm_nome(NOME), uf="BA")]


def op(dia, ent, sai, pdv="BA / LOJA FICTICIA 01", auto="NÃO", nome=NOME):
    return {"DATA DO ROTEIRO": dia, "COLABORADOR": nome, "PONTO DE VENDA": pdv, "HORA ENTRADA": ent,
            "HORA SAIDA": sai, "CHECKOUT SISTEMA": auto}


def calcula(visitas=(), aderencia=(), feriados=(), colabs=None, params=None, **kw):
    base = Base(colaboradores=cadastro() if colabs is None else colabs, visitas=list(visitas),
                aderencia=list(aderencia), feriados=set(feriados))
    return motor.calcular(base, params, INI, FIM, **kw)


# ------------------------------------------------------------------ feriado

def test_feriado_nacional_vindo_da_origem_nao_gera_atraso():
    vs, _ = t.transforma_operacao([op("07/09/2026", "10:00", "17:30"), op("08/09/2026", "10:00", "17:30")],
                                  t.Cadastro(cadastro()))
    (r,) = calcula(vs, feriados={(date(2026, 9, 7), None)})
    assert [x.atraso for x in r.dias] == [0, 120]


# ------------------------------------------------------------------ semana em andamento

def test_semana_em_andamento_nao_gera_alerta_de_aderencia_ponta_a_ponta():
    linhas = [{"MARCA": "MARCA A", "LOJA": "BA / LOJA FICTICIA 01", "UF": "BA", "COLABORADOR": NOME,
               "CONTRATADAS": 10, "REALIZADAS": sem_r, "SEMANA": sem, "ANO": 2026}
              for sem, sem_r in ((38, 10), (39, 0))]
    ader = t.transforma_aderencia(linhas, t.Cadastro(cadastro()), date(2026, 9, 23))  # semana 39 em andamento
    assert [a.semana_fechada for a in ader] == [True, False]
    (r,) = calcula(aderencia=ader)
    assert r.aderencia_pct == 1.0 and not r.alertas


# ------------------------------------------------------------------ CPF ausente e homônimos

def test_sem_cpf_e_sem_cadastro_vira_chave_provisoria_marcada():
    vs, _ = t.transforma_operacao([op("14/09/2026", "08:00", "17:30", nome="Dora Sem Cadastro")], t.Cadastro(cadastro()))
    r = calcula(vs, colabs=[])[0]
    assert r.cpf == "N:DORA SEM CADASTRO" and r.cpf_pendente


def test_homonimos_sem_cpf_na_origem_nao_herdam_cpf_de_nenhum_e_ficam_pendentes():
    cad = t.Cadastro([Colaborador("00000000191", "Ana Teste", "ANA TESTE"), Colaborador("00000000282", "Ana  Teste", "ANA TESTE")])
    vs, _ = t.transforma_operacao([op("14/09/2026", "08:00", "17:30", nome="ANA TESTE")], cad)
    assert vs[0].cpf == "N:ANA TESTE"  # nunca atribui ao CPF errado
    (r,) = calcula(vs, colabs=[])
    assert r.cpf_pendente


def test_chave_provisoria_nao_e_mascaravel_nem_vaza_como_cpf():
    assert util.mascara_cpf("N:ANA TESTE") == ""


# ------------------------------------------------------------------ almoço (PDV NÃO OPERACIONAL)

def test_almoco_nao_e_checkin_nem_conta_como_loja_nem_gera_atraso():
    rows = [op("14/09/2026", "07:00", "07:30", pdv="BA / NÃO OPERACIONAL"),  # "check-in" cedo no almoço
            op("14/09/2026", "08:00", "11:30"), op("14/09/2026", "12:00", "13:00", pdv="BA / NÃO OPERACIONAL"),
            op("14/09/2026", "13:00", "17:30", pdv="BA / LOJA FICTICIA 02")]
    vs, _ = t.transforma_operacao(rows, t.Cadastro(cadastro()))
    (r,) = calcula(vs)
    (dia,) = r.dias
    assert dia.checkin == 480 and dia.atraso == 0 and dia.lojas == 2


def test_so_almoco_no_dia_nao_cria_dia_trabalhado():
    vs, _ = t.transforma_operacao([op("14/09/2026", "12:00", "13:00", pdv="BA / NÃO OPERACIONAL")], t.Cadastro(cadastro()))
    assert calcula(vs) == []


@pytest.mark.xfail(strict=True, reason="A-03: reunião entra em DiaJornada.lojas; CLAUDE.md §4.1 diz que não conta como loja atendida")
def test_reuniao_nao_conta_como_loja_atendida():
    vs, _ = t.transforma_operacao([op("14/09/2026", "08:00", "10:00"), op("14/09/2026", "10:30", "11:30", pdv="BA / REUNIÃO")],
                                  t.Cadastro(cadastro()))
    (r,) = calcula(vs)
    assert r.dias[0].lojas == 1


# ------------------------------------------------------------------ check-out automático

def test_checkout_automatico_no_ultimo_ponto_nao_vira_saida_antecipada():
    rows = [op("14/09/2026", "08:00", "11:00"), op("14/09/2026", "13:00", "17:30", auto="SIM")]
    vs, _ = t.transforma_operacao(rows, t.Cadastro(cadastro()))
    (r,) = calcula(vs, params={**parametros_padrao(), "saida_antecipada_ativa": True})
    d = r.dias[0]
    assert d.auto and d.saida == 0 and d.checkout is None


def test_checkout_automatico_no_meio_do_dia_com_ultimo_manual_mantem_o_manual():
    rows = [op("14/09/2026", "08:00", "11:00", auto="SIM"), op("14/09/2026", "13:00", "17:30")]
    vs, _ = t.transforma_operacao(rows, t.Cadastro(cadastro()))
    (r,) = calcula(vs)
    d = r.dias[0]
    assert d.auto and d.checkout == 1050


# ------------------------------------------------------------------ marcas quinzenais (WD-40 / Botafogo)

def test_semana_impar_de_marca_quinzenal_nao_derruba_a_aderencia():
    def linha(marca, sem, rz):
        return {"MARCA": marca, "LOJA": "BA / LOJA FICTICIA 01", "UF": "BA", "COLABORADOR": NOME,
                "CONTRATADAS": 10, "REALIZADAS": rz, "SEMANA": sem, "ANO": 2026}

    ader = t.transforma_aderencia([linha("WD-40", 37, 0), linha("WD-40", 38, 10), linha("Botafogo", 37, 0)],
                                  t.Cadastro(cadastro()), date(2026, 12, 1))
    (r,) = calcula(aderencia=ader)
    assert r.aderencia_pct == 1.0 and not [a for a in r.alertas if a.tipo == "ader"]


def test_semana_53_de_2026_e_impar_e_quinzenal_nao_contrata():
    assert util.segunda_da_semana_iso(2026, 53) == date(2026, 12, 28)
    linha = {"MARCA": "Botafogo", "LOJA": "BA / L", "COLABORADOR": NOME, "CONTRATADAS": 5, "REALIZADAS": 0, "SEMANA": 53, "ANO": 2026}
    (a,) = t.transforma_aderencia([linha], t.Cadastro(cadastro()), date(2027, 2, 1))
    assert a.contratadas == 0


# ------------------------------------------------------------------ origem com formato alterado

def test_colunas_com_caixa_acento_e_extras_sao_aceitas():
    row = {"data do roteiro": "14/09/2026", "colaborador": NOME, "Ponto de Venda": "BA / L1", "HORA ENTRADA": "08:00",
           "hora saída": "17:30", "checkout sistema": "não", "COLUNA NOVA QUALQUER": "x"}
    vs, desc = t.transforma_operacao([row], t.Cadastro(cadastro()))
    assert desc == 0 and vs[0].checkout == 1050


def test_coluna_obrigatoria_renomeada_descarta_linha_sem_quebrar():
    row = {"DATA": "14/09/2026", "COLAB": NOME, "PONTO DE VENDA": "BA / L1", "HORA ENTRADA": "08:00"}
    vs, desc = t.transforma_operacao([row, op("14/09/2026", "08:00", "17:30")], t.Cadastro(cadastro()))
    assert desc == 1 and len(vs) == 1


def test_linhas_vazias_e_valores_nulos_nao_quebram():
    vs, desc = t.transforma_operacao([{}, {"COLABORADOR": None, "HORA ENTRADA": None}], t.Cadastro([]))
    assert vs == [] and desc == 2
    assert t.transforma_aderencia([{}, {"SEMANA": None}], t.Cadastro([]), date(2026, 9, 1)) == []


def test_cpf_numerico_float_e_texto_com_mascara_viram_a_mesma_chave():
    assert util.normaliza_cpf(191.0) == util.normaliza_cpf("000.000.001-91") == "00000000191"
    assert util.normaliza_cpf("abc") == "" and util.normaliza_cpf("123") == ""


def test_valores_numericos_em_formato_brasileiro():
    assert util.parse_num("1.234,5") == 1234.5 and util.parse_num("93%") == 93.0 and util.parse_num("x") is None


@pytest.mark.xfail(strict=True, raises=ValueError, reason="A-02: parse_data lança ValueError em data impossível; uma linha ruim derruba a transformação do lote")
def test_data_impossivel_nao_derruba_o_lote():
    vs, desc = t.transforma_operacao([op("31/02/2026", "08:00", "17:30"), op("14/09/2026", "08:00", "17:30")], t.Cadastro(cadastro()))
    assert len(vs) == 1 and desc == 1


@pytest.mark.xfail(strict=True, reason="A-02: parse_hora aceita 25:99 (=1599 min) em vez de rejeitar")
def test_hora_impossivel_e_rejeitada():
    assert util.parse_hora("25:99") is None


@pytest.mark.xfail(strict=True, raises=ValueError, reason="A-02: semana ISO inválida (0 ou 54) lança ValueError em transforma_aderencia")
def test_semana_iso_invalida_nao_derruba_o_lote():
    linha = {"MARCA": "M", "LOJA": "BA / L", "COLABORADOR": NOME, "CONTRATADAS": 1, "REALIZADAS": 1, "SEMANA": 54, "ANO": 2026}
    assert t.transforma_aderencia([linha], t.Cadastro([]), date(2027, 1, 1)) == []


def test_visita_unica_com_checkout_antes_da_entrada_nao_quebra_o_motor():
    v = Visita(CPF, date(2026, 9, 14), "BA / L", "loja", 600, 540, False)  # saída antes da entrada (dado ruim)
    (r,) = calcula([v])
    assert r.dias[0].checkin == 600
