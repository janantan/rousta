"""empty message

Revision ID: 0b25ff7c1c67
Revises: 221cfa5c1012
Create Date: 2021-06-06 12:45:33.800132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b25ff7c1c67'
down_revision = '221cfa5c1012'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('vitrin', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'vitrin')
    # ### end Alembic commands ###