"""Esquemas raw, core e app, exatamente como db/modelo.sql.

O DDL fica em db/migrations/sql/0001_modelo.sql, cópia byte a byte de db/modelo.sql
(o teste tests/test_migracoes.py falha se as duas divergirem). Mudou o contrato?
Atualize db/modelo.sql por PR na sessão-mãe e crie uma migração nova; não edite esta.
"""

from pathlib import Path

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

_DDL = Path(__file__).resolve().parent.parent / "sql" / "0001_modelo.sql"


def upgrade() -> None:
    # sa.DDL: não passa pelo parser de parâmetros (o texto tem $$ e barras invertidas)
    op.execute(sa.DDL(_DDL.read_text(encoding="utf-8")))


def downgrade() -> None:
    for esquema in ("app", "core", "raw"):
        op.execute(f"DROP SCHEMA IF EXISTS {esquema} CASCADE")
