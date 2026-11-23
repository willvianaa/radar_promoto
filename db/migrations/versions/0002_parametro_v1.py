"""Parâmetro inicial (parametro_versao nº 1) do db/modelo.md.

Os valores vêm de regras.parametros.PARAMETROS_V1, que o teste compara com o JSON do modelo.md.
Alterar parâmetro = nova versão (linha nova), nunca editar a nº 1.
"""

import json

import sqlalchemy as sa
from alembic import op

from regras.parametros import PARAMETROS_V1

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            "INSERT INTO app.parametro_versao (id, vigente_desde, autor_id, justificativa, valores) "
            "VALUES (1, now(), NULL, :j, CAST(:v AS jsonb))"
        ).bindparams(j="Parâmetros iniciais (db/modelo.md)", v=json.dumps(PARAMETROS_V1, ensure_ascii=False))
    )
    op.execute("SELECT setval(pg_get_serial_sequence('app.parametro_versao', 'id'), 1, true)")


def downgrade() -> None:
    op.execute("DELETE FROM app.parametro_versao WHERE id = 1")
