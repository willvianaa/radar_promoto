"""Parâmetro nº 2: humor negativo inclui Luto, Incomodado, Estressado e Não Valorizado.

Decisão do dono (23/11/2026). A versão nº 1 não é reescrita; esta linha nova passa a valer.
"""

import json

import sqlalchemy as sa
from alembic import op

from regras.parametros import PARAMETROS_V2

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            "INSERT INTO app.parametro_versao (id, vigente_desde, autor_id, justificativa, valores) "
            "VALUES (2, now(), NULL, :j, CAST(:v AS jsonb))"
        ).bindparams(
            j="Humor negativo inclui Luto, Incomodado, Estressado e Não Valorizado (decisão do dono, 23/11/2026)",
            v=json.dumps(PARAMETROS_V2, ensure_ascii=False),
        )
    )
    op.execute("SELECT setval(pg_get_serial_sequence('app.parametro_versao', 'id'), 2, true)")


def downgrade() -> None:
    op.execute("DELETE FROM app.parametro_versao WHERE id = 2")
