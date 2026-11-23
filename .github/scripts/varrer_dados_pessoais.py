"""Varredura de dados pessoais e segredos em arquivos versionados.

Procura padrões de CPF (com e sem máscara, validando os dígitos verificadores),
chaves privadas, tokens de nuvem/GitHub/IA, senhas atribuídas em código e URLs
com credenciais. **Nunca imprime o valor encontrado**: só arquivo, linha (ou
commit) e o tipo do achado, para que o próprio relatório não vaze o dado.

Uso:
    python .github/scripts/varrer_dados_pessoais.py            # arquivos versionados (HEAD)
    python .github/scripts/varrer_dados_pessoais.py --historico # todos os blobs de todos os commits

Sai com código 1 se houver achado bloqueante.

Exceções:
- CPFs fictícios dos fixtures: prefixo ``000.000.00`` (ou ``00000000`` sem máscara),
  conforme CLAUDE.md §2.
- Linha com o comentário ``lgpd: ignorar`` (uso excepcional, justificado no PR e
  revisado pela sessão LGPD e Segurança).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass

IGNORAR = "lgpd: ignorar"

EXTENSOES_BINARIAS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".xlsx", ".xls",
    ".zip", ".gz", ".woff", ".woff2", ".ttf", ".pptx", ".docx",
}

# O próprio scanner e seus testes contêm os padrões de propósito.
CAMINHOS_ISENTOS = {
    ".github/scripts/varrer_dados_pessoais.py",
}

RE_CPF_MASCARA = re.compile(r"(?<![\d.])(\d{3})\.(\d{3})\.(\d{3})-(\d{2})(?![\d])")
RE_CPF_NU = re.compile(r"(?<![\d.\-/])(\d{11})(?![\d])")

SEGREDOS: list[tuple[str, re.Pattern[str]]] = [
    ("chave privada", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY")),
    ("token AWS", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("token GitHub", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{60,}")),
    ("chave Anthropic", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("chave OpenAI", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}")),
    ("token Slack", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("chave Google", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
    ("URL com credencial", re.compile(r"[a-z][a-z0-9+.\-]*://[^/\s:@'\"]+:[^/\s@'\"]{3,}@")),
    (
        "senha/segredo em código",
        re.compile(
            r"(?i)\b(?:password|passwd|senha|secret|segredo|api[_-]?key|token|client[_-]?secret)"
            r"\s*[:=]\s*['\"]([^'\"\s]{8,})['\"]"
        ),
    ),
]

# Valores claramente fictícios aceitos em "senha/segredo em código" e "URL com credencial".
RE_PLACEHOLDER = re.compile(
    r"(?i)(teste|test|exemplo|example|fict|dummy|changeme|troque|placeholder|xxx|\$\{|<|nao_real|não_real|senha_aqui)"
)


@dataclass(frozen=True)
class Achado:
    caminho: str
    local: str  # "linha N" ou "commit abc1234"
    tipo: str
    bloqueante: bool


def cpf_valido(digitos: str) -> bool:
    if len(digitos) != 11 or digitos == digitos[0] * 11:
        return False
    nums = [int(c) for c in digitos]
    for pos in (9, 10):
        soma = sum(nums[i] * (pos + 1 - i) for i in range(pos))
        dv = (soma * 10) % 11 % 10
        if dv != nums[pos]:
            return False
    return True


def ficticio(digitos: str) -> bool:
    return digitos.startswith("00000000")


def varrer_texto(caminho: str, texto: str) -> list[tuple[int, str, bool]]:
    """Devolve (linha, tipo, bloqueante) sem nunca guardar o valor."""
    achados: list[tuple[int, str, bool]] = []
    for n, linha in enumerate(texto.splitlines(), start=1):
        if IGNORAR in linha:
            continue
        for m in RE_CPF_MASCARA.finditer(linha):
            dig = "".join(m.groups())
            if ficticio(dig):
                continue
            if cpf_valido(dig):
                achados.append((n, "CPF formatado (dígitos válidos)", True))
            else:
                achados.append((n, "CPF formatado (dígitos inválidos)", True))
        for m in RE_CPF_NU.finditer(linha):
            dig = m.group(1)
            if ficticio(dig):
                continue
            if cpf_valido(dig):
                achados.append((n, "possível CPF sem máscara (11 dígitos válidos)", True))
        for tipo, rx in SEGREDOS:
            for m in rx.finditer(linha):
                if tipo in ("senha/segredo em código", "URL com credencial") and RE_PLACEHOLDER.search(m.group(0)):
                    continue
                achados.append((n, tipo, True))
    return achados


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def binario(caminho: str, conteudo: bytes) -> bool:
    ext = "." + caminho.rsplit(".", 1)[-1].lower() if "." in caminho else ""
    return ext in EXTENSOES_BINARIAS or b"\x00" in conteudo[:8000]


def varrer_head() -> list[Achado]:
    achados: list[Achado] = []
    for caminho in git("ls-files", "-z").decode("utf-8").split("\0"):
        if not caminho or caminho in CAMINHOS_ISENTOS:
            continue
        try:
            with open(caminho, "rb") as f:
                conteudo = f.read()
        except OSError:
            continue
        if binario(caminho, conteudo):
            continue
        texto = conteudo.decode("utf-8", errors="replace")
        for n, tipo, bloq in varrer_texto(caminho, texto):
            achados.append(Achado(caminho, f"linha {n}", tipo, bloq))
    return achados


def varrer_historico() -> list[Achado]:
    """Cada blob distinto de cada commit, uma vez; relata o primeiro commit em que aparece."""
    commits = git("rev-list", "--all", "--reverse").decode().split()
    vistos: set[str] = set()
    achados: list[Achado] = []
    for commit in commits:
        arvore = git("ls-tree", "-r", "-z", commit).decode("utf-8").split("\0")
        for item in arvore:
            if not item:
                continue
            meta, caminho = item.split("\t", 1)
            _, tipo_obj, blob = meta.split()
            if tipo_obj != "blob" or blob in vistos:
                continue
            vistos.add(blob)
            if caminho in CAMINHOS_ISENTOS:
                continue
            conteudo = git("cat-file", "blob", blob)
            if binario(caminho, conteudo):
                continue
            texto = conteudo.decode("utf-8", errors="replace")
            tipos = {(tipo, bloq) for _, tipo, bloq in varrer_texto(caminho, texto)}
            for tipo, bloq in sorted(tipos):
                achados.append(Achado(caminho, f"commit {commit[:7]}", tipo, bloq))
    return achados


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--historico", action="store_true", help="varre todos os commits")
    args = ap.parse_args()

    achados = varrer_historico() if args.historico else varrer_head()
    if not achados:
        print("Nenhum padrão de CPF ou segredo encontrado.")
        return 0

    agrupado: dict[tuple[str, str], list[str]] = defaultdict(list)
    for a in achados:
        agrupado[(a.caminho, a.tipo)].append(a.local)
    print("Achados (o valor nunca é exibido):")
    for (caminho, tipo), locais in sorted(agrupado.items()):
        mostra = ", ".join(locais[:5]) + (f" (+{len(locais) - 5})" if len(locais) > 5 else "")
        print(f"  {caminho}: {tipo} — {len(locais)} ocorrência(s): {mostra}")
    print(
        "\nNão copie o valor para PR, issue ou chat. Remova o dado, use CPF fictício "
        "(000.000.00x-xx) e, se já entrou no histórico, avise a sessão LGPD e Segurança."
    )
    return 1 if any(a.bloqueante for a in achados) else 0


if __name__ == "__main__":
    sys.exit(main())
