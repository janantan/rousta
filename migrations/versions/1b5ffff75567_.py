"""empty message

Revision ID: 1b5ffff75567
Revises: 14419ed3afe2
Create Date: 2021-05-22 00:52:03.813653

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1b5ffff75567'
down_revision = '14419ed3afe2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('categoryId', sa.String(length=200), nullable=True))
    op.add_column('product', sa.Column('rostaakLocation', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.drop_column('product', 'category')
    op.drop_column('product', 'city')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('city', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('product', sa.Column('category', sa.VARCHAR(length=300), autoincrement=False, nullable=True))
    op.drop_column('product', 'rostaakLocation')
    op.drop_column('product', 'categoryId')
    # ### end Alembic commands ###