"""Added dementia rating.

Revision ID: 827395fac4eb
Revises: a223e0599e2b
Create Date: 2024-01-03 13:22:35.738296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '827395fac4eb'
down_revision = 'a223e0599e2b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('image', 'tags')
    op.drop_column('image', 'recognizedText')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('image', sa.Column('recognizedText', sa.VARCHAR(length=1000), nullable=True))
    op.add_column('image', sa.Column('tags', sa.VARCHAR(length=1000), nullable=True))
    # ### end Alembic commands ###