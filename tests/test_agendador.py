from datetime import datetime
from zoneinfo import ZoneInfo

from ingestor.agendador import FUSO, proxima_execucao

SP = ZoneInfo("America/Sao_Paulo")


def test_antes_das_5_roda_no_mesmo_dia():
    agora = datetime(2026, 3, 10, 4, 0, tzinfo=SP)
    assert proxima_execucao(agora) == datetime(2026, 3, 10, 5, 0, tzinfo=SP)


def test_exatamente_as_5_roda_no_dia_seguinte():
    agora = datetime(2026, 3, 10, 5, 0, tzinfo=SP)
    assert proxima_execucao(agora) == datetime(2026, 3, 11, 5, 0, tzinfo=SP)


def test_depois_das_5_roda_no_dia_seguinte():
    agora = datetime(2026, 3, 10, 17, 30, tzinfo=SP)
    assert proxima_execucao(agora) == datetime(2026, 3, 11, 5, 0, tzinfo=SP)


def test_converte_instante_utc_para_horario_de_sao_paulo():
    # 07:30 UTC = 04:30 em São Paulo (UTC-3, sem horário de verão desde 2019)
    agora_utc = datetime(2026, 3, 10, 7, 30, tzinfo=ZoneInfo("UTC"))
    resultado = proxima_execucao(agora_utc)
    assert resultado.astimezone(FUSO) == datetime(2026, 3, 10, 5, 0, tzinfo=SP)
