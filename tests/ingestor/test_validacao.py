
from openpyxl import Workbook

from ingestor.validacao import FORMATO_ALTERADO, OK, validar_arquivo

CAB_ADER = ["MARCA", "LOJA", "SUPERVISOR", "UF", "COLABORADOR", "CONTRATADAS", "REALIZADAS", "AJUSTADAS", "SEMANA", "ANO"]


def _xlsx(tmp_path, linhas, nome="x.xlsx"):
    wb = Workbook()
    for lin in linhas:
        wb.active.append(lin)
    p = tmp_path / nome
    wb.save(p)
    return p


def test_csv_ok_descarta_colunas_fora_do_schema_e_deduplica(fix):
    r = validar_arquivo(fix / "colaboradores_ok.csv", "colaboradores")
    assert r.status == OK
    assert r.linhas_aceitas == 2 and r.duplicadas == 1
    assert all("TELEFONE PESSOAL" not in lin and "ID" in lin for lin in r.linhas)
    assert len(r.sha256) == 64


def test_cabecalho_fora_da_primeira_linha_e_nome_normalizado(fix):
    r = validar_arquivo(fix / "humor_ok.xlsx", "humor")
    assert r.status == OK and r.linhas_aceitas == 2
    assert set(r.linhas[0]) == {"NOME DO COLABORADOR", "DATA", "HUMOR"}


def test_coluna_obrigatoria_ausente_e_formato_alterado(fix):
    r = validar_arquivo(fix / "colaboradores_sem_cpf.csv", "colaboradores")
    assert r.status == FORMATO_ALTERADO and "CPF" in r.motivo and r.linhas == []
    r = validar_arquivo(fix / "humor_sem_coluna.xlsx", "humor")
    assert r.status == FORMATO_ALTERADO and "HUMOR" in r.motivo


def test_arquivo_vazio_e_formato_alterado(fix):
    r = validar_arquivo(fix / "humor_vazio.xlsx", "humor")
    assert r.status == FORMATO_ALTERADO and r.linhas == []


def test_cabecalho_alem_da_linha_15_nao_e_achado(tmp_path):
    p = _xlsx(tmp_path, [[None]] * 15 + [["NOME DO COLABORADOR", "DATA", "HUMOR"], ["A", "d", "Feliz"]])
    assert validar_arquivo(p, "humor").status == FORMATO_ALTERADO


def test_tipo_alterado_acima_de_2_por_cento(tmp_path):
    def lin(i, uf):
        return ["M", f"SP / L{i}", "S", uf, "ANA FICTICIA", 4, 1, 1, 40, 2026]

    ok = _xlsx(tmp_path, [CAB_ADER] + [lin(i, "SP") for i in range(100)], "ok.xlsx")
    assert validar_arquivo(ok, "aderencia").status == OK
    um = _xlsx(tmp_path, [CAB_ADER] + [lin(i, "x1" if i == 0 else "SP") for i in range(100)], "um.xlsx")
    r = validar_arquivo(um, "aderencia")
    assert r.status == OK and r.linhas_aceitas == 99 and r.linhas_descartadas == 1
    tres = _xlsx(tmp_path, [CAB_ADER] + [lin(i, "x1" if i < 3 else "SP") for i in range(100)], "tres.xlsx")
    assert validar_arquivo(tres, "aderencia").status == FORMATO_ALTERADO


def test_operacao_descarta_visita_sem_entrada(tmp_path):
    cab = ["DATA DO ROTEIRO", "COLABORADOR", "COLABORADOR SUPERIOR", "ESTADO", "PONTO DE VENDA",
           "HORA ENTRADA", "HORA SAIDA", "CHECKOUT SISTEMA"]
    p = _xlsx(tmp_path, [
        cab,
        ["20/11/2026", "ANA FICTICIA", "B", "SP", "SP / LOJA 1", "08:00", "09:00", "NÃO"],
        ["20/11/2026", "ANA FICTICIA", "B", "SP", "SP / LOJA 2", None, None, "NÃO"],
    ])
    r = validar_arquivo(p, "operacao")
    assert r.status == OK and r.linhas_aceitas == 1 and r.sem_entrada == 1


def test_extras_entram_na_linha_do_pdoh(tmp_path):
    cab = ["#", "Colaborador", "Marca", "Superior", "UF", "Tempo (HH:MM)", "Segundos", "%", "Dias"]
    p = _xlsx(tmp_path, [cab, [1, "ANA FICTICIA", "M", "B", "SP", "01:00", 3600, 12.5, 3]])
    ex = {"categoria": "prod", "periodo_ini": "2026-11-01", "periodo_fim": "2026-11-14"}
    r = validar_arquivo(p, "pdoh", extras=ex)
    assert r.linhas[0]["categoria"] == "prod"


def test_arquivo_corrompido_nao_levanta(tmp_path):
    p = tmp_path / "x.xlsx"
    p.write_bytes(b"nao e xlsx")
    assert validar_arquivo(p, "humor").status == FORMATO_ALTERADO
