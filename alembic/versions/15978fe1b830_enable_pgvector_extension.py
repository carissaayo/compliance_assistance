"""enable pgvector extension

Revision ID: 15978fe1b830
Revises: 
Create Date: 2026-07-28 15:36:07.575215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15978fe1b830'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
   op.execute("CREATE EXTENSION IF NOT EXISTS vector")
  


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")
