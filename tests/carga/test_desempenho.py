"""Desempenho do motor em volume (A-01 da QA). Opt-in: ``RADAR_CARGA=1 pytest tests/carga/test_desempenho.py -s``.

Meta: 1.000 colaboradores × 60 dias em até 10 s (``RADAR_LIMITE_S`` muda o limite em máquinas mais lentas).
Fica fora da execução padrão para não alongar nem tornar instável o CI.
"""

import os
import time

import pytest

from regras import motor
from tests.carga.gerador import gerar_base

pytestmark = pytest.mark.skipif(not os.getenv("RADAR_CARGA"), reason="teste de carga: defina RADAR_CARGA=1")


def test_motor_1000_colaboradores_60_dias_dentro_da_meta():
    base, meta = gerar_base(1000, 60, 2026)
    t0 = time.perf_counter()
    res = motor.calcular(base, None, meta.ini, meta.fim)
    dt = time.perf_counter() - t0
    print(f"\ncalcular: {dt:.2f} s para {len(res)} colaboradores")
    assert len(res) == 1000
    assert dt <= float(os.getenv("RADAR_LIMITE_S", "10"))
