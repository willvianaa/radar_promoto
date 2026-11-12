"""
Procura fotos duplicadas nos ZIPs de fotos exportados do Involves (dados/fotos/*.zip).

  - IDÊNTICA: mesmo conteúdo de arquivo (SHA-256).
  - MUITO PARECIDA: hash perceptual (dHash 64 bits) com diferença de até LIMITE bits.
    Atenção: fotos de uma mesma gôndola tiradas do mesmo ponto ficam parecidas
    sem serem repetidas. Toda parecida precisa de conferência visual.

Cada foto se chama IDdaPesquisa_IDdaFoto.jpg. O cruzamento com loja, data e formulário
usa dados/involves/pesquisas_*.csv.

Saída: dados/radar/fotos_duplicadas.csv e um resumo no terminal.
Nada daqui vai para o GitHub: a pasta dados/ está no .gitignore.

Uso:  python ferramentas/detectar_fotos_duplicadas.py [LIMITE]      (padrão: 3)
"""
import csv
import glob
import hashlib
import io
import os
import re
import sys
import zipfile
from collections import defaultdict

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS = os.path.join(RAIZ, "dados", "fotos")
PESQ = os.path.join(RAIZ, "dados", "involves")
SAIDA = os.path.join(RAIZ, "dados", "radar", "fotos_duplicadas.csv")
LIMITE = int(sys.argv[1]) if len(sys.argv) > 1 else 3


def dhash(img):
    g = img.convert("L").resize((9, 8), Image.LANCZOS)
    px = list(g.getdata())
    bits = 0
    for y in range(8):
        for x in range(8):
            bits = (bits << 1) | (1 if px[y * 9 + x] > px[y * 9 + x + 1] else 0)
    return bits


def promotor_do_zip(nome):
    m = re.match(r"fotos_\d+_(.+?)_\d{4}-\d{2}-\d{2}", nome)
    return m.group(1).replace("_", " ").upper() if m else nome


def carregar_pesquisas():
    meta = {}
    for arq in glob.glob(os.path.join(PESQ, "pesquisas_*.csv")):
        with open(arq, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f, delimiter=";"):
                meta[r["ID"]] = (r["PDV"].strip(), r["Solicitação"][:10], r["Formulário"].strip(), r["Responsável"].strip())
    return meta


def main():
    meta = carregar_pesquisas()
    fotos = []
    for zp in sorted(glob.glob(os.path.join(FOTOS, "*.zip"))):
        zn = os.path.basename(zp)
        with zipfile.ZipFile(zp) as z:
            for e in z.infolist():
                if e.is_dir():
                    continue
                dados = z.read(e.filename)
                try:
                    img = Image.open(io.BytesIO(dados))
                    h = dhash(img)
                    dim = img.size
                except Exception:
                    h, dim = None, None
                m = re.match(r"(\d+)_(\d+)", os.path.basename(e.filename))
                pid = m.group(1) if m else ""
                info = meta.get(pid, ("", "", "", ""))
                fotos.append({"zip": zn, "arq": os.path.basename(e.filename), "sha": hashlib.sha256(dados).hexdigest(),
                              "h": h, "dim": dim, "pid": pid, "pdv": info[0], "data": info[1], "form": info[2],
                              "prom": info[3] or promotor_do_zip(zn)})
    print("Fotos lidas:", len(fotos), "| sem hash (arquivo ilegível):", sum(1 for f in fotos if f["h"] is None))

    # grupos idênticos
    por_sha = defaultdict(list)
    for f in fotos:
        por_sha[f["sha"]].append(f)
    grupos = [("IDÊNTICA", g) for g in por_sha.values() if len(g) > 1]
    em_identica = {id(f) for _, g in grupos for f in g}

    # grupos muito parecidos (união-busca simples), ignorando o que já é idêntico
    unicas = [g[0] for g in por_sha.values() if g[0]["h"] is not None]
    pai = list(range(len(unicas)))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    for i in range(len(unicas)):
        for j in range(i + 1, len(unicas)):
            if bin(unicas[i]["h"] ^ unicas[j]["h"]).count("1") <= LIMITE:
                pai[raiz(i)] = raiz(j)
    comp = defaultdict(list)
    for i in range(len(unicas)):
        comp[raiz(i)].append(unicas[i])
    for membros in comp.values():
        if len(membros) > 1:
            todos = [f for m in membros for f in por_sha[m["sha"]]]
            grupos.append(("MUITO PARECIDA", todos))

    linhas, resumo = [], defaultdict(lambda: defaultdict(int))
    for n, (tipo, g) in enumerate(sorted(grupos, key=lambda x: -len(x[1])), 1):
        pesquisas = {f["pid"] for f in g}
        promotores = {f["prom"] for f in g}
        escopo = ("mesma pesquisa" if len(pesquisas) == 1 else
                  "pesquisas diferentes, mesmo promotor" if len(promotores) == 1 else
                  "promotores diferentes")
        for f in g:
            linhas.append([n, tipo, escopo, len(g), f["prom"], f["pid"], f["pdv"], f["data"], f["form"], f["zip"], f["arq"]])
            resumo[f["prom"]][(tipo, escopo)] += 1
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Grupo", "Tipo", "Escopo", "Fotos no grupo", "Promotor", "ID da pesquisa", "PDV", "Data da pesquisa",
                    "Formulário", "ZIP", "Arquivo"])
        w.writerows(linhas)
    print("Grupos:", len(grupos), "| fotos em grupos:", len(linhas), "| limite de bits:", LIMITE)
    for prom, d in sorted(resumo.items()):
        print(" ", prom)
        for (tipo, escopo), n in sorted(d.items()):
            print("     %-15s %-40s %4d fotos" % (tipo, escopo, n))
    print("Relatório:", SAIDA)


if __name__ == "__main__":
    main()
