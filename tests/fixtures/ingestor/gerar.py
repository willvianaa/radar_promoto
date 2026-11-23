"""Gera as planilhas FICTÍCIAS desta pasta (nomes inventados, CPFs inválidos de propósito).

Os testes chamam `gerar(destino)` (o .gitignore barra planilhas no repositório).
Uso manual: python tests/fixtures/ingestor/gerar.py
"""

from pathlib import Path

from openpyxl import Workbook

AQUI = Path(__file__).parent
DESTINO = AQUI


def xlsx(nome, linhas):
    wb = Workbook()
    ws = wb.active
    for lin in linhas:
        ws.append(lin)
    wb.save(DESTINO / nome)


def csv(nome, linhas):
    texto = "\n".join(";".join(map(str, lin)) for lin in linhas) + "\n"
    (DESTINO / nome).write_text(texto, encoding="utf-8-sig")


def gerar(destino=AQUI):
    global DESTINO
    DESTINO = Path(destino)
    DESTINO.mkdir(parents=True, exist_ok=True)
    csv("colaboradores_ok.csv", [
        ["ID", "NOME DO COLABORADOR", "USUARIO ATIVO", "COLABORADOR SUPERIOR", "CPF", "UF", "TELEFONE PESSOAL"],
        [1, "ANA FICTICIA", "SIM", "BRUNO FICTICIO", "000.000.001-91", "SP", "11 00000-0001"],
        [2, "CARLOS FICTICIO", "SIM", "BRUNO FICTICIO", "000.000.002-72", "RJ", "21 00000-0002"],
        [2, "CARLOS FICTICIO", "SIM", "BRUNO FICTICIO", "000.000.002-72", "RJ", "21 00000-0002"],
    ])
    csv("colaboradores_sem_cpf.csv", [
        ["ID", "NOME DO COLABORADOR", "USUARIO ATIVO", "COLABORADOR SUPERIOR", "UF"],
        [1, "ANA FICTICIA", "SIM", "BRUNO FICTICIO", "SP"],
    ])
    xlsx("humor_ok.xlsx", [
        ["Relatório de humor"], ["Gerado em 22/11/2026"], [],
        ["Nome do  Colaborador", "Data", "Humor", "Observação livre"],
        ["ANA FICTICIA", "20/11/2026", "Feliz", "x"],
        ["CARLOS FICTICIO", "20/11/2026", "Cansado", "y"],
    ])
    xlsx("humor_sem_coluna.xlsx", [["NOME DO COLABORADOR", "DATA"], ["ANA FICTICIA", "20/11/2026"]])
    xlsx("humor_vazio.xlsx", [["NOME DO COLABORADOR", "DATA", "HUMOR"]])
    return DESTINO


if __name__ == "__main__":
    gerar()
