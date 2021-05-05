"""empty message

Revision ID: 2452b337349d
Revises: 191439ea12db
Create Date: 2021-05-04 01:09:29.626510

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2452b337349d'
down_revision = '191439ea12db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shop', sa.Column('imageList', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.drop_column('shop', 'image')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shop', sa.Column('image', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.drop_column('shop', 'imageList')
    # ### end Alembic commands ###
