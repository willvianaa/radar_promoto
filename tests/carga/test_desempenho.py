"""Fumaça de desempenho do motor. O teto é folgado de propósito (CI varia); a linha de base
real fica em docs/qa/desempenho.md e se mede com ``python -m tests.carga.medir``."""

import time

from regras import motor
from tests.carga.gerador import gerar_base

TETO_100x30_S = 60.0


def test_motor_100_colaboradores_30_dias_dentro_do_teto():
    base, meta = gerar_base(100, 30, semente=11)
    t = time.perf_counter()
    res = motor.calcular(base, None, meta.ini, meta.fim)
    dur = time.perf_counter() - t
    assert len(res) >= 90
    assert dur < TETO_100x30_S, f"motor levou {dur:.1f}s (teto {TETO_100x30_S}s); ver docs/qa/desempenho.md"


def test_resultado_identico_entre_execucoes():
    """Determinismo (CLAUDE.md §4.7): mesma entrada + mesmos parâmetros = mesmo resultado."""
    base, meta = gerar_base(60, 30, semente=12)
    a = motor.calcular(base, None, meta.ini, meta.fim)
    b = motor.calcular(base, None, meta.ini, meta.fim)
    assert [(r.cpf, r.nivel, r.risco, r.score) for r in a] == [(r.cpf, r.nivel, r.risco, r.score) for r in b]
