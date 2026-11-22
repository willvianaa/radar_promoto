"""Valida os contratos do repositório: schemas/*.json (JSON Schema 2020-12) e api/openapi.yaml.

Uso: python scripts/validar_contratos.py
Sai com código 1 se algum contrato for inválido.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import yaml
from openapi_spec_validator import validate

RAIZ = Path(__file__).resolve().parent.parent


def validar_schemas() -> list[str]:
    erros: list[str] = []
    arquivos = sorted((RAIZ / "schemas").glob("*.schema.json"))
    if not arquivos:
        return ["nenhum schema encontrado em schemas/"]
    for arquivo in arquivos:
        try:
            documento = json.loads(arquivo.read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator.check_schema(documento)
        except (json.JSONDecodeError, jsonschema.exceptions.SchemaError) as exc:
            erros.append(f"{arquivo.relative_to(RAIZ)}: {exc}")
    return erros


def validar_openapi() -> list[str]:
    caminho = RAIZ / "api" / "openapi.yaml"
    try:
        documento = yaml.safe_load(caminho.read_text(encoding="utf-8"))
        validate(documento)
    except Exception as exc:  # noqa: BLE001 - qualquer falha de validação é relatada
        return [f"{caminho.relative_to(RAIZ)}: {exc}"]
    return []


def main() -> int:
    erros = validar_schemas() + validar_openapi()
    if erros:
        for erro in erros:
            print(f"ERRO {erro}")
        return 1
    print("contratos válidos: schemas/*.schema.json e api/openapi.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
