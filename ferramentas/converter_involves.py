"""
Converte as exportações do Involves para o formato que o Radar Promotor lê em "Atualizar dados".

Lê (em dados/involves):
  - pesquisas_*.csv            (Relatório de pesquisas, separador ";")
  - operacao_*.xlsx            (Relatório de Check-in do Painel de Visitas)
  - humor_*.xlsx               (Relatório de Humor)
  - colaboradores_cpf.csv      (lista de colaboradores com CPF)

Grava (em dados/radar):
  - pesquisas_radar.csv, operacao_radar.csv, humor_radar.csv

O CPF é buscado pelo nome do colaborador na lista de colaboradores.
Nenhum dado real deve ir para o GitHub: a pasta dados/ está no .gitignore.

Uso:  python ferramentas/converter_involves.py
"""
import csv
import glob
import os
import re
import sys
import unicodedata
import warnings

import openpyxl

warnings.filterwarnings("ignore")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA = os.path.join(RAIZ, "dados", "involves")
SAIDA = os.path.join(RAIZ, "dados", "radar")


def norm(s):
    s = unicodedata.normalize("NFD", str(s or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(s.upper().split())


def data_br(v):
    """datetime, 'dd/mm/aaaa hh:mm' ou 'aaaa-mm-dd ...' -> 'dd/mm/aaaa'."""
    if v is None or v == "":
        return ""
    if hasattr(v, "strftime"):
        return v.strftime("%d/%m/%Y")
    s = str(v).strip()
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", s)
    if m:
        return "%s/%s/%s" % m.groups()
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    return "%s/%s/%s" % (m.group(3), m.group(2), m.group(1)) if m else ""


def hora(v):
    if v is None or v == "":
        return ""
    if hasattr(v, "strftime"):
        return v.strftime("%H:%M")
    m = re.search(r"(\d{1,2}):(\d{2})", str(v))
    return "%02d:%s" % (int(m.group(1)), m.group(2)) if m else ""


def carregar_cpf():
    caminho = os.path.join(ENTRADA, "colaboradores_cpf.csv")
    mapa = {}
    if not os.path.exists(caminho):
        print("Aviso: colaboradores_cpf.csv não encontrado. Os arquivos sairão sem CPF.")
        return mapa
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r.get("CPF"):
                mapa[norm(r["NOME DO COLABORADOR"])] = r["CPF"]
    return mapa


def escrever(nome, cabecalho, linhas):
    os.makedirs(SAIDA, exist_ok=True)
    caminho = os.path.join(SAIDA, nome)
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(cabecalho)
        w.writerows(linhas)
    return caminho


def pesquisas(cpf):
    vistos, linhas, sem_cpf = set(), [], set()
    for arq in sorted(glob.glob(os.path.join(ENTRADA, "pesquisas_*.csv"))):
        with open(arq, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f, delimiter=";"):
                if r["ID"] in vistos:
                    continue
                vistos.add(r["ID"])
                nome = r["Responsável"].strip()
                form = r["Formulário"].strip()
                m = re.match(r"\[([^\]]+)\]\s*(.*)", form)
                cliente, tipo = (m.group(1), m.group(2)) if m else ("", form)
                pdv = r["PDV"].strip()
                uf = pdv[:2] if re.match(r"^[A-Z]{2} / ", pdv) else ""
                c = cpf.get(norm(nome), "")
                if not c:
                    sem_cpf.add(norm(nome))
                linhas.append([nome, c, r["Colaborador superior"].strip(), uf,
                               data_br(r["Solicitação"]), pdv, cliente, tipo, r["Status"].strip()])
    escrever("pesquisas_radar.csv",
             ["Colaborador", "CPF", "Supervisor", "UF", "Data", "PDV", "Cliente", "Tipo de pesquisa", "Status"],
             linhas)
    return len(linhas), len(sem_cpf)


def operacao(cpf):
    vistos, linhas, sem_cpf, sem_checkin = set(), [], set(), 0
    for arq in sorted(glob.glob(os.path.join(ENTRADA, "operacao_*.xlsx"))):
        ws = openpyxl.load_workbook(arq).worksheets[0]
        todas = list(ws.iter_rows(values_only=True))
        cab = [norm(x) for x in todas[0]]
        ix = {}
        for i, h in enumerate(cab):
            ix.setdefault(h, i)
        for r in todas[1:]:
            ent, sai = r[ix["HORA ENTRADA"]], r[ix["HORA SAIDA"]]
            if not ent:
                sem_checkin += 1
                continue
            nome = str(r[ix["COLABORADOR"]] or "").strip()
            chave = (nome, r[ix["PONTO DE VENDA"]], ent, sai)
            if chave in vistos:
                continue
            vistos.add(chave)
            c = cpf.get(norm(nome), "")
            if not c:
                sem_cpf.add(norm(nome))
            sistema = norm(r[ix["CHECKOUT SISTEMA"]]) == "SIM"
            linhas.append([nome, c, str(r[ix["COLABORADOR SUPERIOR"]] or "").strip(),
                           str(r[ix["ESTADO"]] or "").strip(), data_br(r[ix["DATA DO ROTEIRO"]]),
                           str(r[ix["PONTO DE VENDA"]] or "").strip(), hora(ent), hora(sai),
                           "Realizado pelo sistema" if sistema else "Manual"])
    escrever("operacao_radar.csv",
             ["Colaborador", "CPF", "Supervisor", "UF", "Data", "PDV", "Check-in", "Check-out", "Tipo de check-out"],
             linhas)
    return len(linhas), len(sem_cpf), sem_checkin


def humor(cpf):
    linhas, sem_cpf = [], set()
    for arq in sorted(glob.glob(os.path.join(ENTRADA, "humor_*.xlsx"))):
        ws = openpyxl.load_workbook(arq).worksheets[0]
        todas = list(ws.iter_rows(values_only=True))
        topo = next(i for i, r in enumerate(todas) if any(norm(x) == "NOME DO COLABORADOR" for x in r))
        cab = [norm(x) for x in todas[topo]]
        i_nome, i_hum, i_data = cab.index("NOME DO COLABORADOR"), cab.index("HUMOR"), cab.index("DATA")
        for r in todas[topo + 1:]:
            if not r[i_nome] or not r[i_hum]:
                continue
            nome = str(r[i_nome]).strip()
            c = cpf.get(norm(nome), "")
            if not c:
                sem_cpf.add(norm(nome))
            linhas.append([nome, c, data_br(r[i_data]), str(r[i_hum]).strip()])
    escrever("humor_radar.csv", ["Colaborador", "CPF", "Data", "Humor"], linhas)
    return len(linhas), len(sem_cpf)


def main():
    if not os.path.isdir(ENTRADA):
        sys.exit("Pasta não encontrada: " + ENTRADA)
    cpf = carregar_cpf()
    n, s = pesquisas(cpf)
    print("pesquisas_radar.csv : %6d linhas | nomes sem CPF: %d" % (n, s))
    n, s, sc = operacao(cpf)
    print("operacao_radar.csv  : %6d linhas | nomes sem CPF: %d | linhas sem check-in (não entram): %d" % (n, s, sc))
    n, s = humor(cpf)
    print("humor_radar.csv     : %6d linhas | nomes sem CPF: %d" % (n, s))
    print("Arquivos em:", SAIDA)


if __name__ == "__main__":
    main()
