"""Merge parameters and template bboxes branches

Revision ID: 8eef5b5ca999
Revises: 9a3cc1ff951a, f8470d5029e5
Create Date: 2025-08-15 11:44:38.040082

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "8eef5b5ca999"
down_revision: Union[str, None] = ("9a3cc1ff951a", "f8470d5029e5")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
