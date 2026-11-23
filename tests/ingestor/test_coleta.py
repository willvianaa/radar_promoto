import datetime as dt

from openpyxl import Workbook

from ingestor.coleta import coletar_origem
from tests.ingestor.test_gravacao import ConnFalsa


def _humor(tmp_path, nome, n):
    wb = Workbook()
    wb.active.append(["NOME DO COLABORADOR", "DATA", "HUMOR"])
    for i in range(n):
        wb.active.append([f"PESSOA FICTICIA {i}", "20/11/2026", "Feliz"])
    p = tmp_path / nome
    wb.save(p)
    return p


def test_janela_no_limite_e_dividida_ao_meio(tmp_path):
    pedidos = []

    def baixar(ini, fim):
        pedidos.append((ini, fim))
        n = 10_000 if (fim - ini).days >= 3 else 5  # janelas de 4+ dias "truncam"
        return [(_humor(tmp_path, f"h{len(pedidos)}.xlsx", n), None)]

    c = ConnFalsa()
    st = coletar_origem(c, "humor", baixar, dt.date(2026, 11, 1), dt.date(2026, 11, 4), None)
    assert pedidos[0] == (dt.date(2026, 11, 1), dt.date(2026, 11, 4))
    assert pedidos[1:] == [(dt.date(2026, 11, 1), dt.date(2026, 11, 2)), (dt.date(2026, 11, 3), dt.date(2026, 11, 4))]
    assert st == ["gravado", "gravado"]


def test_um_dia_no_limite_abre_alerta_e_nao_grava(tmp_path):
    c = ConnFalsa()
    st = coletar_origem(c, "humor", lambda i, f: [(_humor(tmp_path, "x.xlsx", 10_000), None)],
                        dt.date(2026, 11, 1), dt.date(2026, 11, 1), None)
    assert st == ["formato_alterado"]
    assert len(c.chamadas) == 1 and "ingestao_alerta" in c.chamadas[0][0]


def test_arquivo_baixado_e_apagado_apos_gravar_e_mantido_se_formato_alterado(tmp_path):
    ok = _humor(tmp_path, "ok.xlsx", 3)
    coletar_origem(ConnFalsa(), "humor", lambda i, f: [(ok, None)], dt.date(2026, 11, 1), dt.date(2026, 11, 1), None)
    assert not ok.exists()
    ruim = tmp_path / "ruim.xlsx"
    ruim.write_bytes(b"nao e xlsx")
    coletar_origem(ConnFalsa(), "humor", lambda i, f: [(ruim, None)], dt.date(2026, 11, 1), dt.date(2026, 11, 1), None)
    assert ruim.exists()  # fica no storage (fora do git) para diagnóstico
