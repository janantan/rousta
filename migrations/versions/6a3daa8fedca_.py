"""empty message

Revision ID: 6a3daa8fedca
Revises: 8ab9cde72021
Create Date: 2021-05-04 01:36:54.538892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a3daa8fedca'
down_revision = '8ab9cde72021'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('category_categoryId_key', 'category', type_='unique')
    op.drop_index('ix_product_productId', table_name='product')
    op.drop_index('ix_user_userId', table_name='user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_user_userId', 'user', ['userId'], unique=False)
    op.create_index('ix_product_productId', 'product', ['productId'], unique=True)
    op.create_unique_constraint('category_categoryId_key', 'category', ['categoryId'])
    # ### end Alembic commands ###
