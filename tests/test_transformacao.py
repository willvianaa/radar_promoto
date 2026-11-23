"""Transformação raw → core (dados 100% fictícios)."""

from datetime import date

from regras import transformacao as t
from regras import util
from regras.tipos import Colaborador


def colab(cpf, nome, **kw):
    return Colaborador(cpf=cpf, nome=nome, nome_norm=util.norm_nome(nome), **kw)


def test_norm_nome():
    assert util.norm_nome("  José   da  Conceição ") == "JOSE DA CONCEICAO"
    assert util.norm_nome(None) == ""


def test_cpf_normaliza_e_mascara():
    assert util.normaliza_cpf("000.000.001-91") == "00000000191"
    assert util.normaliza_cpf(12345678901) == "12345678901"
    assert util.normaliza_cpf(191) == "00000000191"  # número de planilha perde os zeros à esquerda
    assert util.normaliza_cpf("123") == ""
    assert util.mascara_cpf("00000000191") == "***.000.001-**"
    assert util.mascara_cpf("N:FULANO") == ""


def test_cpf_numerico_da_planilha_recupera_zeros():
    assert util.normaliza_cpf(191) == "00000000191"


def test_heranca_de_cpf_pelo_nome_normalizado():
    cad = t.Cadastro([colab("00000000191", "Joana Modelo Pereira")])
    assert cad.resolver("JOANA  MODELO pereira") == ("00000000191", False)
    assert cad.resolver("Joana Modelo Pereira", "000.000.009-99") == ("00000000999", False)  # CPF da origem vale mais
    assert cad.resolver("Sem Cadastro") == ("N:SEM CADASTRO", True)


def test_homonimos_nao_herdam_cpf():
    cad = t.Cadastro([colab("00000000191", "Ana Teste"), colab("00000000282", "ANA  TESTE")])
    assert cad.resolver("Ana Teste") == ("N:ANA TESTE", True)


def test_status_pesquisa():
    s = t.status_pesquisa
    assert s("Respondido") == "R" and s("Realizada") == "R" and s("Concluído") == "R"
    assert s("Expirado") == "E" and s("Não realizada") == "E" and s("NÃO RESPONDIDA") == "E"
    assert s("Pendente") == "P" and s("") == "P"


def test_jornada_cadastrada_mantem_duracao():
    assert t.jornada_do_texto("INÍCIO 07H") == (420, 990)
    assert t.jornada_do_texto("") == (None, None)
    assert t.jornada_do_texto("Folguista") == (None, None)


def test_colaboradores_sem_cpf_ficam_pendentes_e_supervisor_resolve():
    rows = [
        {"NOME DO COLABORADOR": "Chefe Fictício", "CPF": "000.000.007-27", "UF": "BA", "USUARIO ATIVO": "SIM"},
        {"NOME DO COLABORADOR": "Sem Cpf Teste", "CPF": "", "COLABORADOR SUPERIOR": "chefe  fictício", "UF": "BA", "USUARIO ATIVO": "NÃO"},
        {"NOME DO COLABORADOR": "Com Cpf Teste", "CPF": "000.000.008-18", "COLABORADOR SUPERIOR": "chefe  fictício", "USUARIO ATIVO": "SIM"},
    ]
    cs = {c.nome: c for c in t.transforma_colaboradores(rows)}
    assert cs["Sem Cpf Teste"].cpf_pendente and cs["Sem Cpf Teste"].cpf == "N:SEM CPF TESTE" and not cs["Sem Cpf Teste"].ativo
    assert cs["Com Cpf Teste"].supervisor_cpf == "00000000727"


def test_operacao_almoco_reuniao_auto_e_descartes():
    cad = t.Cadastro([colab("00000000191", "Joana Modelo Pereira")])
    base = {"DATA DO ROTEIRO": "14/09/2026", "COLABORADOR": "Joana Modelo Pereira", "CHECKOUT SISTEMA": "NÃO"}
    rows = [
        {**base, "PONTO DE VENDA": "BA / LOJA FICTICIA 01", "HORA ENTRADA": "08:00", "HORA SAIDA": "11:30"},
        {**base, "PONTO DE VENDA": "BA / NÃO OPERACIONAL", "HORA ENTRADA": "12:00", "HORA SAIDA": "13:00"},
        {**base, "PONTO DE VENDA": "BA / REUNIÃO", "HORA ENTRADA": "14:00", "HORA SAIDA": "15:00"},
        {**base, "PONTO DE VENDA": "BA / LOJA FICTICIA 02", "HORA ENTRADA": "15:30", "HORA SAIDA": "17:30", "CHECKOUT SISTEMA": "SIM"},
        {**base, "PONTO DE VENDA": "BA / LOJA FICTICIA 02", "HORA ENTRADA": "15:30", "HORA SAIDA": "17:30", "CHECKOUT SISTEMA": "SIM"},  # duplicada
        {**base, "PONTO DE VENDA": "BA / LOJA FICTICIA 03", "HORA ENTRADA": "", "HORA SAIDA": ""},  # visita não iniciada
    ]
    vs, descartadas = t.transforma_operacao(rows, cad)
    assert descartadas == 2
    assert [v.tipo_pdv for v in vs] == ["loja", "nao_operacional", "reuniao", "loja"]
    assert [v.checkout_auto for v in vs] == [False, False, False, True]
    assert vs[0].cpf == "00000000191" and vs[0].checkin == 480 and vs[0].checkout == 690


def test_operacao_aceita_serial_do_excel():
    cad = t.Cadastro([])
    rows = [{"DATA DO ROTEIRO": 46279, "COLABORADOR": "Fulano Teste", "PONTO DE VENDA": "BA / L", "HORA ENTRADA": 46279.3333333,
             "HORA SAIDA": 46279.5, "CHECKOUT SISTEMA": ""}]
    (v,), _ = t.transforma_operacao(rows, cad)
    assert v.data == date(2026, 9, 14) and v.checkin == 480 and v.checkout == 720


def test_atividades_formulario_e_status():
    cad = t.Cadastro([])
    rows = [{"ID": "X1", "Formulário": "[MARCA A] Preço", "PDV": "BA / L", "Responsável": "Fulano Teste",
             "Solicitação": "14/09/2026 08:00", "Status": "Expirada", "Justificada?": "Sim", "Total de Fotos": "3"}]
    (a,) = t.transforma_atividades(rows, cad)
    assert (a.cliente, a.tipo, a.status, a.justificada, a.fotos, a.data) == ("MARCA A", "Preço", "E", True, 3, date(2026, 9, 14))


def test_humor_negativo_pela_lista_de_parametros():
    cad = t.Cadastro([])
    rows = [{"NOME DO COLABORADOR": "Fulano Teste", "DATA": "14/09/2026", "HUMOR": "Doente"},
            {"NOME DO COLABORADOR": "Fulano Teste", "DATA": "15/09/2026", "HUMOR": "Feliz"},
            {"NOME DO COLABORADOR": "Fulano Teste", "DATA": "16/09/2026", "HUMOR": "Luto"}]  # pendente de decisão do RH
    hs = t.transforma_humor(rows, cad, ["Cansado", "Doente"])
    assert [h.negativo for h in hs] == [True, False, False]


def test_faltas_tipos():
    assert t.tipo_falta("Injustificada") == "I"
    assert t.tipo_falta("Justificada") == "J"
    assert t.tipo_falta("Atestado") == "A"
    assert t.tipo_falta("Afastamento") == "F"
    assert t.tipo_falta("", "consulta") == "J"
    cad = t.Cadastro([])
    (f,) = t.transforma_faltas([{"CPF": "000.000.001-91", "Colaborador": "Fulano", "Data": "10/09/2026", "Tipo": "Atestado"}], cad)
    assert f.cpf == "00000000191" and f.tipo == "A"


def test_afastamento_com_dias_expande():
    cad = t.Cadastro([])
    fs = t.transforma_faltas([{"Colaborador": "Fulano Teste", "Data": "10/09/2026", "Tipo": "Afastamento", "Dias": 3}], cad)
    assert [f.data.day for f in fs] == [10, 11, 12]


def test_aderencia_teto_por_linha_semana_fechada_e_sem_colaborador():
    cad = t.Cadastro([colab("00000000191", "Joana Modelo Pereira")])

    def r(sem, ct, rz, marca="MARCA A", nome="Joana Modelo Pereira"):
        return {"MARCA": marca, "LOJA": "BA / LOJA FICTICIA 01", "UF": "BA", "COLABORADOR": nome,
                "CONTRATADAS": ct, "REALIZADAS": rz, "SEMANA": sem, "ANO": 2026}

    rows = [r(37, 4, 6), r(38, 10, 7), r(39, 10, 0), r(38, 5, 0, nome="SEM COLABORADOR")]
    a37, a38, a39, sem_col = t.transforma_aderencia(rows, cad, date(2026, 9, 21))  # segunda-feira da semana 39
    assert a37.realizadas == 6 and a37.realizadas_lim == 4          # teto na linha
    assert a37.semana_ini == date(2026, 9, 7)
    assert a38.semana_fechada                                        # terminou domingo 20/09
    assert not a39.semana_fechada                                    # semana 39 em andamento
    assert sem_col.cpf is None


def test_aderencia_semana_so_fecha_depois_do_domingo():
    cad = t.Cadastro([])
    linha = [{"MARCA": "M", "LOJA": "BA / L", "COLABORADOR": "Fulano Teste", "CONTRATADAS": 1, "REALIZADAS": 1, "SEMANA": 38, "ANO": 2026}]
    assert not t.transforma_aderencia(linha, cad, date(2026, 9, 20))[0].semana_fechada  # domingo ainda é a semana
    assert t.transforma_aderencia(linha, cad, date(2026, 9, 21))[0].semana_fechada


def test_marcas_quinzenais_so_contratam_em_semana_par():
    cad = t.Cadastro([])

    def r(marca, sem):
        return {"MARCA": marca, "LOJA": "BA / L", "COLABORADOR": "Fulano Teste", "CONTRATADAS": 4, "REALIZADAS": 4, "SEMANA": sem, "ANO": 2026}

    impar, par, comum = t.transforma_aderencia([r("WD-40", 37), r("WD-40", 38), r("Botafogo", 37)], cad, date(2026, 12, 1))[0:3]
    assert impar.contratadas == 0 and impar.realizadas_lim == 0
    assert par.contratadas == 4
    assert comum.contratadas == 0
    assert t.transforma_aderencia([r("MARCA A", 37)], cad, date(2026, 12, 1))[0].contratadas == 4


def test_pdoh_junta_as_quatro_categorias():
    cad = t.Cadastro([colab("00000000191", "Joana Modelo Pereira")])
    cat = {k: [{"Colaborador": "Joana Modelo Pereira", "Segundos": v, "Dias": 5}] for k, v in
           {"prod": 100, "desl": 20, "ocio": 10, "hnr": 5}.items()}
    (p,) = t.transforma_pdoh(cat, cad, date(2026, 9, 1), date(2026, 9, 25))
    assert (p.cpf, p.seg_produtivo, p.seg_deslocamento, p.seg_ocio, p.seg_nao_registrado, p.dias) == ("00000000191", 100, 20, 10, 5, 5)


def test_fotos_exigem_hash():
    cad = t.Cadastro([])
    rows = [{"Colaborador": "Fulano Teste", "Data": "14/09/2026", "PDV": "BA / L", "Arquivo": "a.jpg", "SHA256": "AB" * 32, "Latitude": "-12,9"},
            {"Colaborador": "Fulano Teste", "Data": "14/09/2026", "PDV": "BA / L", "Arquivo": "b.jpg"}]
    (f,) = t.transforma_fotos(rows, cad)
    assert f.sha256 == "ab" * 32 and f.lat == -12.9


def test_aderencia_linhas_invalidas_sao_descartadas_e_contadas():
    cad = t.Cadastro([])

    def r(sem, ano=2026):
        return {"MARCA": "M", "LOJA": "BA / L", "COLABORADOR": "Fulano Teste", "CONTRATADAS": 1, "REALIZADAS": 1, "SEMANA": sem, "ANO": ano}

    descartes: list[int] = []
    ok = t.transforma_aderencia([r(0), r(38), r(54), r(38, ano=99999), {"LOJA": "BA / L"}], cad, date(2027, 1, 1), descartes)
    assert len(ok) == 1 and ok[0].semana_ini == date(2026, 9, 14)
    assert descartes == [0, 2, 3, 4]


def test_datas_e_horas_impossiveis_viram_none():
    assert util.parse_data("31/02/2026") is None and util.parse_data("2026-13-01") is None and util.parse_data("00/00/0000") is None
    assert util.parse_data("29/02/2028") == date(2028, 2, 29)
    assert util.parse_hora("25:99") is None and util.parse_hora("24:00") is None and util.parse_hora("23:59") == 1439
    assert util.parse_hora("08:05") == 485
