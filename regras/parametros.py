"""Parâmetros versionados (versão nº 1 = db/modelo.md) e a regra de limites."""

from __future__ import annotations

import copy

PARAMETROS_V1: dict = {
    "escala": {"ini": "08:00", "fim": "17:30"},
    "tolerancia_atraso_min": 15,
    "tolerancia_saida_min": 15,
    "saida_antecipada_ativa": False,
    "meta1": 85,
    "meta2": 93,
    "corte_ader_dossie": 93,
    "dist_foto_m": 300,
    "cerca_rota_m": 200,
    "humor_negativo": ["Cansado", "Sobrecarregado", "Triste", "Doente"],
    "limites": {
        "atraso": [4, 7, 10],
        "saida": [4, 7, 10],
        "checkout_auto": [5, 8, 10],
        "pesq_expiradas_pct": [20, 30, 45],
        "pesq_min": 20,
        "dias_sem_atividade": [0, 2, 4],
        "faltas_injust": [0, 1, 3],
        "fotos_indicio": [0, 1, 3],
        "visitas_pendentes": [0, 1, 10],
        "dias_fuga_rota": [0, 3, 10],
        "humor_pct": 40,
        "humor_seq": 3,
        "carga_semana": 44,
        "queda_ader_pp": 5,
    },
    "nivel": {"critico_soma": 9, "critico_sev3": 2, "alto_soma": 5, "atencao_soma": 3},
}


def parametros_padrao() -> dict:
    """Cópia independente da versão 1 (o motor nunca altera o dicionário recebido)."""
    return copy.deepcopy(PARAMETROS_V1)


def severidade(valor: float, limites: list[float]) -> int:
    """Limites [a, b, c]: valor ≥ c → 3; ≥ b → 2; ≥ a (e a > 0) → 1; senão 0.

    Um limite 0 desliga aquela faixa (igual ao protótipo: ``t[2] && v >= t[2]``).
    """
    a, b, c = limites
    if c and valor >= c:
        return 3
    if b and valor >= b:
        return 2
    if a and valor >= a:
        return 1
    return 0
