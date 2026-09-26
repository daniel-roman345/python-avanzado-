"""add authentication fields to users

Revision ID: a3f14b9c2e01
Revises: e61a53a3b60c
Create Date: 2026-09-26 00:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3f14b9c2e01"
down_revision: Union[str, Sequence[str], None] = "e61a53a3b60c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agrega la columna hashed_password a la tabla users."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "hashed_password",
                sa.String(length=255),
                nullable=False,
                server_default="",
            )
        )

    # Se quita el server_default para que futuros insert deban aportar el hash
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column(
            "hashed_password",
            existing_type=sa.String(length=255),
            server_default=None,
        )


def downgrade() -> None:
    """Elimina la columna hashed_password."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("hashed_password")
