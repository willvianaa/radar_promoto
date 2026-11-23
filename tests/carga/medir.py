"""Mede o tempo do motor de regras sobre o volume real sintético.

Uso (a partir da raiz do repositório)::

    python -m tests.carga.medir                 # 1.000 colaboradores × 60 dias, 3 repetições
    python -m tests.carga.medir --colaboradores 200 --dias 30 --repeticoes 1

Imprime uma linha de tabela pronta para ``docs/qa/desempenho.md``.
"""

from __future__ import annotations

import argparse
import platform
import statistics
import time

from regras import motor
from tests.carga.gerador import gerar_base


def medir(n: int, dias: int, semente: int, repeticoes: int) -> dict:
    t0 = time.perf_counter()
    base, meta = gerar_base(n, dias, semente)
    t_gerar = time.perf_counter() - t0
    tempos = []
    for _ in range(repeticoes):
        t = time.perf_counter()
        res = motor.calcular(base, None, meta.ini, meta.fim)
        tempos.append(time.perf_counter() - t)
    niveis = {k: sum(1 for r in res if r.nivel == k) for k in "CATN"}
    return {"meta": meta, "gerar_s": t_gerar, "tempos": tempos, "n_resultados": len(res), "niveis": niveis}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--colaboradores", type=int, default=1000)
    ap.add_argument("--dias", type=int, default=60)
    ap.add_argument("--semente", type=int, default=2026)
    ap.add_argument("--repeticoes", type=int, default=3)
    a = ap.parse_args()
    r = medir(a.colaboradores, a.dias, a.semente, a.repeticoes)
    m = r["meta"]
    print(f"Python {platform.python_version()} · {platform.system()} {platform.machine()}")
    print(f"colaboradores={m.n_colaboradores} dias={m.dias} semente={m.semente} impressão={m.impressao}")
    print("linhas:", ", ".join(f"{k}={v:,}".replace(",", ".") for k, v in m.contagens.items()))
    print(f"geração dos dados: {r['gerar_s']:.2f} s")
    print("motor (s):", ", ".join(f"{t:.2f}" for t in r["tempos"]),
          f"· mediana {statistics.median(r['tempos']):.2f} s · resultados {r['n_resultados']} · níveis {r['niveis']}")


if __name__ == "__main__":
    main()
