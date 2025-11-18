"""add property security tags

Revision ID: dc7a59b43e27
Revises: 8f5b8f7e2c6d
Create Date: 2025-10-19 12:27:12.918975

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dc7a59b43e27"
down_revision: str | Sequence[str] | None = "8f5b8f7e2c6d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "propertytype",
        sa.Column("security_tags", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("propertytype", "security_tags")
