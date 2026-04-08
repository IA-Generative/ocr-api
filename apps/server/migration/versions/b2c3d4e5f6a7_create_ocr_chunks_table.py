"""create ocr_chunks table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-02 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ocr_chunks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("content_hash", sa.String(), nullable=False),
        sa.Column("page_nums", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("bbox_indices", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("model_name", sa.String(), nullable=False),
        sa.Column("vector", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("vector_size", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ocr_chunks_content_hash", "ocr_chunks", ["content_hash"])


def downgrade() -> None:
    op.drop_index("ix_ocr_chunks_content_hash", table_name="ocr_chunks")
    op.drop_table("ocr_chunks")
