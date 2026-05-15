"""add user language

Revision ID: 8b9f1d2c3a4e
Revises: 279e466a1dac
Create Date: 2026-05-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8b9f1d2c3a4e"
down_revision: Union[str, Sequence[str], None] = "279e466a1dac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("language", sa.String(length=2), nullable=False, server_default="uz"),
    )
    op.alter_column("users", "language", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "language")
