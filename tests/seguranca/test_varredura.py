"""A varredura de CPF e segredos do CI (.github/scripts/varrer_dados_pessoais.py) detecta o que
deve e nunca imprime o valor.

Os valores "proibidos" são montados em tempo de teste (CPF gerado, token concatenado), para que
este arquivo não vire achado da própria varredura.
"""

from __future__ import annotations

import importlib.util
import subprocess  # nosec B404 - só executa o próprio script, sem shell
import sys
from pathlib import Path

import pytest

from tests.seguranca._apoio import cpfs_validos, formatar

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / ".github" / "scripts" / "varrer_dados_pessoais.py"

_spec = importlib.util.spec_from_file_location("varrer_dados_pessoais", SCRIPT)
varredura = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = varredura
_spec.loader.exec_module(varredura)

CPF = cpfs_validos(1, semente=7)[0]


def _tipos(texto: str) -> list[str]:
    return [tipo for _, tipo, _ in varredura.varrer_texto("x.py", texto)]


def test_cpf_valido_formatado_e_sem_mascara():
    assert _tipos(f"cpf = '{formatar(CPF)}'") == ["CPF formatado (dígitos válidos)"]
    assert _tipos(f"cpf = '{CPF}'") == ["possível CPF sem máscara (11 dígitos válidos)"]


def test_cpf_formatado_com_digitos_invalidos_tambem_bloqueia():
    invalido = CPF[:9] + str((int(CPF[9]) + 1) % 10) + CPF[10]
    assert _tipos(formatar(invalido)) == ["CPF formatado (dígitos inválidos)"]


@pytest.mark.parametrize("ficticio", ["000.000.001-91", "000.000.009-99", "00000000191"])
def test_cpf_ficticio_dos_fixtures_passa(ficticio):
    assert _tipos(f"cpf = '{ficticio}'") == []


def test_comentario_de_excecao():
    assert _tipos(f"{formatar(CPF)}  # lgpd: ignorar") == []


@pytest.mark.parametrize(
    "texto,tipo",
    [
        ("gh" + "p_" + "A1b2" * 9, "token GitHub"),
        ("AK" + "IA" + "ABCDEFGHIJKLMNOP", "token AWS"),
        ("-----BEGIN " + "PRIVATE KEY-----", "chave privada"),
        ("postgres://" + "usuario:" + "s3nhaR3al@host/db", "URL com credencial"),
        ("senha" + ' = "' + "Kx9#mQ2vLp" + '"', "senha/segredo em código"),
    ],
)
def test_segredos(texto, tipo):
    assert tipo in _tipos(texto)


def test_placeholder_de_exemplo_passa():
    assert _tipos('senha = "troque_esta_senha"') == []
    assert _tipos("postgres://" + "usuario:" + "teste123@localhost/db") == []


def test_relatorio_nunca_imprime_o_valor(tmp_path):
    """Roda o script num repositório git temporário com um CPF e confere a saída."""
    git = ["git", "-c", "user.name=teste", "-c", "user.email=teste@example.invalid", "-c", "commit.gpgsign=false"]
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)  # nosec B603 B607
    (tmp_path / "dados.txt").write_text(f"colaborador {formatar(CPF)} e {CPF}\n", encoding="utf-8")
    subprocess.run([*git, "-C", str(tmp_path), "add", "."], check=True)  # nosec B603 B607
    subprocess.run([*git, "-C", str(tmp_path), "commit", "-q", "-m", "x"], check=True)  # nosec B603 B607

    for args in ([], ["--historico"]):
        r = subprocess.run(  # nosec B603
            [sys.executable, str(SCRIPT), *args], cwd=tmp_path, capture_output=True, text=True, encoding="utf-8"
        )
        assert r.returncode == 1, "achado de CPF tem de reprovar"
        saida = r.stdout + r.stderr
        assert "dados.txt" in saida
        assert CPF not in saida.replace(".", "").replace("-", "")
        assert CPF[3:9] not in saida.replace(".", "")
