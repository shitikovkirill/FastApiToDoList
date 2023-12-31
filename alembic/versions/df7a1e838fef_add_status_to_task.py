"""Add status to task

Revision ID: df7a1e838fef
Revises: 53d4cd737c42
Create Date: 2023-09-18 11:10:15.565269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'df7a1e838fef'
down_revision: Union[str, None] = '53d4cd737c42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('status', sa.Enum('completed', 'not_completed', name='taskstatus'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task', 'status')
    # ### end Alembic commands ###
