"""first init

Revision ID: 04cd1f6d4542
Revises: 615c928d2e1b
Create Date: 2025-06-18 21:12:21.849841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '04cd1f6d4542'
down_revision: Union[str, None] = '615c928d2e1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
