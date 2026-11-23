"""Coluna senha_hash em app.usuario (login por e-mail e senha até o SSO, Q-06).

Guarda só o hash argon2; nunca a senha. Nulo = usuário sem login por senha.
"""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE app.usuario ADD COLUMN senha_hash text")


def downgrade() -> None:
    op.execute("ALTER TABLE app.usuario DROP COLUMN senha_hash")
