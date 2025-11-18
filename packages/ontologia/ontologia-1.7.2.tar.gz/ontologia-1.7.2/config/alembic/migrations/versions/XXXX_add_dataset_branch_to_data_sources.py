"""Add dataset_branch_rid to ObjectTypeDataSource

Revision ID: XXXX
Revises: 3d47cf7fa5eb
Create Date: 2025-03-10 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "XXXX"
down_revision = "3d47cf7fa5eb"
branch_labels = None
depends_on = None


def upgrade():
    # Add the new column
    op.add_column(
        "objecttypedatasource", sa.Column("dataset_branch_rid", sa.String(), nullable=True)
    )

    # Create the foreign key constraint
    op.create_foreign_key(
        "fk_objecttypedatasource_dataset_branch_rid",
        "objecttypedatasource",
        "datasetbranch",
        ["dataset_branch_rid"],
        ["rid"],
    )

    # Create an index on the new column
    op.create_index(
        "ix_objecttypedatasource_dataset_branch_rid", "objecttypedatasource", ["dataset_branch_rid"]
    )


def downgrade():
    op.drop_constraint(
        "fk_objecttypedatasource_dataset_branch_rid", "objecttypedatasource", type_="foreignkey"
    )
    op.drop_index("ix_objecttypedatasource_dataset_branch_rid", "objecttypedatasource")
    op.drop_column("objecttypedatasource", "dataset_branch_rid")
