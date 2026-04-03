"""remove task_id from annotations table

Revision ID: a1b2c3d4e5f6
Revises: 564486764bcd
Create Date: 2026-04-02 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "564486764bcd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f("ix_annotations_task_id"), table_name="annotations")
    op.drop_column("annotations", "task_id")


def downgrade() -> None:
    op.add_column("annotations", sa.Column("task_id", sa.String(), nullable=True))
    op.create_index(op.f("ix_annotations_task_id"), "annotations", ["task_id"], unique=False)
