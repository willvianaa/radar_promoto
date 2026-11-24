"""
Procura indícios de foto nos ZIPs exportados do Involves (dados/fotos/*.zip) que não dependem de comparar fotos:

  - FOTO PRETA: imagem quase toda escura (brilho médio baixo e pouca variação). É o caso do
    promotor que lança foto preta no abastecimento ou no horário da visita.

"Foto da foto" (foto de outro celular mostrando um abastecimento) não tem detecção automática
confiável aqui: no protótipo ela aparece quando a foto foi tirada fora do horário da visita, ou
quando alguém marca o indício na coluna "Indício" da planilha.

Cada foto se chama IDdaPesquisa_IDdaFoto.jpg; loja, data e formulário vêm de dados/involves/pesquisas_*.csv.
Saída: dados/radar/fotos_indicios.csv (formato da base de fotos do protótipo, com a coluna "Indício")
e cópia das fotos marcadas em radar_v3/fotos/ para conferência na tela. Nada daqui vai para o GitHub.

Uso:  python ferramentas/detectar_fotos_indicios.py [BRILHO_MAX] [VARIACAO_MAX]   (padrão: 28 e 22)
"""
import csv
import glob
import hashlib
import io
import os
import re
import sys
import zipfile

from PIL import Image, ImageStat

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detectar_fotos_duplicadas import FOTOS, RAIZ, carregar_pesquisas, promotor_do_zip  # noqa: E402

SAIDA = os.path.join(RAIZ, "dados", "radar", "fotos_indicios.csv")
COPIA = os.path.join(RAIZ, "radar_v3", "fotos")
BRILHO_MAX = float(sys.argv[1]) if len(sys.argv) > 1 else 28
VARIACAO_MAX = float(sys.argv[2]) if len(sys.argv) > 2 else 22


def escura(img):
    g = img.convert("L")
    g.thumbnail((256, 256))
    st = ImageStat.Stat(g)
    media, desvio = st.mean[0], st.stddev[0]
    return (media <= BRILHO_MAX and desvio <= VARIACAO_MAX) or media <= 12, media, desvio


def main():
    meta = carregar_pesquisas()
    linhas, lidas, ilegiveis = [], 0, 0
    os.makedirs(COPIA, exist_ok=True)
    for zp in sorted(glob.glob(os.path.join(FOTOS, "*.zip"))):
        zn = os.path.basename(zp)
        with zipfile.ZipFile(zp) as z:
            for e in z.infolist():
                if e.is_dir():
                    continue
                dados = z.read(e.filename)
                lidas += 1
                try:
                    preta, _, _ = escura(Image.open(io.BytesIO(dados)))
                except Exception:
                    ilegiveis += 1
                    continue
                if not preta:
                    continue
                arq = os.path.basename(e.filename)
                m = re.match(r"(\d+)_(\d+)", arq)
                pdv, data, form, resp = meta.get(m.group(1) if m else "", ("", "", "", ""))
                linhas.append([resp or promotor_do_zip(zn), data, pdv, form, hashlib.sha256(dados).hexdigest()[:16], arq, "Foto preta"])
                with open(os.path.join(COPIA, arq), "wb") as f:
                    f.write(dados)
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Colaborador", "Data", "PDV", "Tipo de pesquisa", "Hash", "Arquivo", "Indício"])
        w.writerows(linhas)
    print(f"Fotos lidas: {lidas} | ilegíveis: {ilegiveis} | fotos pretas: {len(linhas)}")
    print("Saída:", os.path.relpath(SAIDA, RAIZ))


if __name__ == "__main__":
    main()
