from contextlib import contextmanager

from ingestor.gravacao import gravar
from ingestor.validacao import validar_arquivo



class Cur:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def executemany(self, sql, params):
        self.conn.chamadas.append((sql, list(params)))


class Res:
    def __init__(self, linha):
        self.linha = linha

    def fetchone(self):
        return self.linha


class ConnFalsa:
    """Registra o SQL; sem Postgres no CI, o SQL real não é executado aqui."""

    def __init__(self, existente=None):
        self.chamadas, self.existente = [], existente

    @contextmanager
    def transaction(self):
        yield

    def cursor(self):
        return Cur(self)

    def execute(self, sql, params=()):
        self.chamadas.append((sql, params))
        if sql.startswith("SELECT"):
            return Res(self.existente)
        return Res((7,))


def test_formato_alterado_so_abre_alerta(fix):
    r = validar_arquivo(fix / "humor_sem_coluna.xlsx", "humor")
    c = ConnFalsa()
    g = gravar(c, r, fix / "humor_sem_coluna.xlsx")
    assert g.status == "formato_alterado"
    assert len(c.chamadas) == 1 and "app.ingestao_alerta" in c.chamadas[0][0]


def test_ok_grava_carga_e_linhas(fix):
    r = validar_arquivo(fix / "humor_ok.xlsx", "humor")
    c = ConnFalsa()
    g = gravar(c, r, fix / "humor_ok.xlsx")
    assert g.status == "gravado" and g.carga_id == 7
    assert any("INSERT INTO raw.carga" in s for s, _ in c.chamadas)
    assert [n for _, n, _ in c.chamadas[-1][1]] == [1, 2]


def test_mesmo_arquivo_nao_regrava(fix):
    r = validar_arquivo(fix / "humor_ok.xlsx", "humor")
    c = ConnFalsa(existente=(3,))
    g = gravar(c, r, fix / "humor_ok.xlsx")
    assert g.status == "duplicado" and g.carga_id == 3
    assert not any("INSERT" in s for s, _ in c.chamadas)
