import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fixtures" / "ingestor"))
from gerar import gerar  # noqa: E402


@pytest.fixture(scope="session")
def fix(tmp_path_factory):
    """Planilhas fictícias geradas em pasta temporária (o .gitignore barra xlsx/csv no repositório)."""
    return gerar(tmp_path_factory.mktemp("planilhas"))
