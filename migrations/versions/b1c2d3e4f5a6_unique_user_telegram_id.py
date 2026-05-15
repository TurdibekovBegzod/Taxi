"""unique user telegram id

Revision ID: b1c2d3e4f5a6
Revises: 8b9f1d2c3a4e
Create Date: 2026-05-14 03:35:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "8b9f1d2c3a4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DELETE FROM users
        WHERE telegram_id IS NOT NULL
          AND id NOT IN (
              SELECT MAX(id)
              FROM users
              WHERE telegram_id IS NOT NULL
              GROUP BY telegram_id
          )
    """)
    op.create_index(
        "ix_users_telegram_id_unique",
        "users",
        ["telegram_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_users_telegram_id_unique", table_name="users")
