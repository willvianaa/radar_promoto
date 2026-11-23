"""Validador de exports: lê CSV/XLSX, confere o formato contra `schemas/*.schema.json`.

Regras (schemas/README.md): cabeçalho nas 15 primeiras linhas; colunas obrigatórias; tipos (mais de 2%
de linhas fora do tipo = formato alterado); colunas fora do schema são descartadas (mínimo necessário,
LGPD); duplicidade pela `x-chave-unica`. Nada aqui grava no banco nem registra valores de células em log.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"
LINHAS_PROCURA_CABECALHO = 15
LIMITE_TIPO_INVALIDO = 0.02
LIMITE_LINHAS_EXPORT = 10_000  # a origem corta nesse valor: >= isso é tratado como export truncado

OK = "ok"
FORMATO_ALTERADO = "formato_alterado"

# Linha sem este campo não entra (schemas/operacao: visita não iniciada); é contada no relatório.
CAMPO_DESCARTE_SE_VAZIO = {"operacao": "HORA ENTRADA"}


def normalizar(texto: Any) -> str:
    """Maiúsculas, sem acento, espaços simples (regra de comparação de cabeçalhos)."""
    s = unicodedata.normalize("NFKD", str(texto if texto is not None else ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.upper().split())


@dataclass
class Resultado:
    origem: str
    status: str  # 'ok' | 'formato_alterado'
    motivo: str | None = None
    sha256: str | None = None
    linhas: list[dict[str, Any]] = field(default_factory=list)
    linhas_lidas: int = 0
    linhas_descartadas: int = 0
    duplicadas: int = 0
    sem_entrada: int = 0
    excedeu_limite: bool = False  # export no limite da origem (possível truncamento): fatiar mais

    @property
    def linhas_aceitas(self) -> int:
        return len(self.linhas)


def carregar_schema(origem: str) -> dict:
    caminho = SCHEMAS_DIR / f"{origem}.schema.json"
    if not caminho.is_file():
        raise ValueError(f"origem desconhecida: {origem!r}")
    return json.loads(caminho.read_text(encoding="utf-8"))


def sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _celula(v: Any) -> Any:
    if isinstance(v, dt.datetime):
        return v.isoformat(sep=" ")
    if isinstance(v, (dt.date, dt.time)):
        return v.isoformat()
    if isinstance(v, str):
        v = v.strip()
    return v


def _ler_matriz(caminho: Path, schema: dict) -> list[list[Any]]:
    fmt = schema.get("x-formato", {})
    sufixo = caminho.suffix.lower()
    if sufixo == ".csv":
        with caminho.open(newline="", encoding=fmt.get("encoding", "utf-8-sig")) as f:
            sep = fmt.get("separador", ";")
            return [[_celula(c) for c in lin] for lin in csv.reader(f, delimiter=sep)]
    if sufixo in (".xlsx", ".xlsm"):
        from openpyxl import load_workbook

        wb = load_workbook(caminho, read_only=True, data_only=True)
        try:
            aba = fmt.get("aba", 0)
            ws = wb.worksheets[aba if isinstance(aba, int) else 0]
            return [[_celula(c) for c in lin] for lin in ws.iter_rows(values_only=True)]
        finally:
            wb.close()
    raise ValueError(f"extensão não suportada: {sufixo}")


def _vazio(v: Any) -> bool:
    return v is None or (isinstance(v, str) and v == "")


def _tipo_ok(valor: Any, prop: dict) -> bool:
    """Confere um valor contra a propriedade do schema. Texto numérico vale como número (CSV)."""
    if "type" not in prop and "enum" not in prop and "pattern" not in prop:
        return True
    cand = [valor]
    if isinstance(valor, str):
        for conv in (int, lambda s: float(s.replace(",", "."))):
            try:
                cand.append(conv(valor))
            except ValueError:
                pass
    elif isinstance(valor, float) and valor.is_integer():
        cand.append(int(valor))
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        cand.append(str(valor))
    for c in cand:
        try:
            jsonschema.validate(c, prop, cls=jsonschema.Draft202012Validator)
            return True
        except jsonschema.ValidationError:
            continue
    return False


def validar_arquivo(
    caminho: Path | str, origem: str, extras: dict[str, Any] | None = None, *, minimo_linhas: int = 1
) -> Resultado:
    """Valida um export. `extras` (ex.: categoria/período do PDOH) entra em cada linha aceita.

    Retorna `Resultado` com status 'ok' ou 'formato_alterado' (e `motivo`, sem valores de células).
    """
    caminho = Path(caminho)
    schema = carregar_schema(origem)
    res = Resultado(origem=origem, status=OK, sha256=sha256_arquivo(caminho))

    def alterado(motivo: str) -> Resultado:
        res.status, res.motivo, res.linhas = FORMATO_ALTERADO, motivo, []
        return res

    try:
        matriz = _ler_matriz(caminho, schema)
    except Exception as e:  # arquivo corrompido, aba inexistente etc.
        return alterado(f"arquivo ilegível ({type(e).__name__})")

    obrigatorias = {normalizar(c): c for c in schema["x-colunas-obrigatorias"]}
    props = {normalizar(k): k for k in schema["properties"]}
    idx_cab = None
    for i, lin in enumerate(matriz[:LINHAS_PROCURA_CABECALHO]):
        if set(obrigatorias) <= {normalizar(c) for c in lin if not _vazio(c)}:
            idx_cab = i
            break
    if idx_cab is None:
        achados: set[str] = set()
        for lin in matriz[:LINHAS_PROCURA_CABECALHO]:
            achados |= {normalizar(c) for c in lin if not _vazio(c)}
        faltam = sorted(obrigatorias[n] for n in obrigatorias if n not in achados)
        return alterado(
            "cabeçalho não encontrado nas 15 primeiras linhas; colunas ausentes: "
            + ", ".join(faltam or ["(em linhas diferentes)"])
        )

    cab = matriz[idx_cab]
    mapa: dict[int, str] = {}  # índice da coluna -> nome canônico (só colunas do schema)
    for j, nome in enumerate(cab):
        canon = props.get(normalizar(nome)) if not _vazio(nome) else None
        if canon and canon not in mapa.values():
            mapa[j] = canon

    corpo = [lin for lin in matriz[idx_cab + 1 :] if any(not _vazio(c) for c in lin)]
    res.linhas_lidas = len(corpo)
    if len(corpo) < minimo_linhas:
        return alterado("arquivo sem linhas de dados")
    if len(corpo) >= LIMITE_LINHAS_EXPORT:
        res.excedeu_limite = True
        return alterado(f"export no limite de {LIMITE_LINHAS_EXPORT} linhas (possível truncamento); fatiar por período")

    chave = schema["x-chave-unica"]
    campo_descarte = CAMPO_DESCARTE_SE_VAZIO.get(origem)
    vistos: set[tuple] = set()
    tipo_invalido = 0
    aceitas: list[dict[str, Any]] = []
    for lin in corpo:
        linha = {nome: (lin[j] if j < len(lin) else None) for j, nome in mapa.items()}
        if any(not _vazio(v) and not _tipo_ok(v, schema["properties"][k]) for k, v in linha.items()):
            tipo_invalido += 1
            continue
        if campo_descarte and _vazio(linha.get(campo_descarte)):
            res.sem_entrada += 1
            continue
        if extras:
            linha.update(extras)
        k = tuple(linha.get(c) for c in chave)
        if k in vistos:
            res.duplicadas += 1
            continue
        vistos.add(k)
        aceitas.append(linha)

    if tipo_invalido / len(corpo) > LIMITE_TIPO_INVALIDO:
        return alterado(f"tipo de dado alterado em {tipo_invalido} de {len(corpo)} linhas (limite 2%)")
    res.linhas = aceitas
    res.linhas_descartadas = len(corpo) - len(aceitas)
    return res
