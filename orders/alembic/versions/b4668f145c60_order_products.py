"""order_products

Revision ID: b4668f145c60
Revises: dd33cb03d01f
Create Date: 2022-08-17 12:36:00.438166

"""

# revision identifiers, used by Alembic.
revision = 'b4668f145c60'
down_revision = 'dd33cb03d01f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'order_details',
        'product_id',
        existing_type=sa.String(),
        nullable=False,
        type_=sa.Integer(),
        postgresql_using='product_id::integer'
    )
    op.create_table('products',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('redis_id', sa.String(length=256), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('passenger_capacity', sa.Integer(), nullable=False),
    sa.Column('maximum_speed', sa.Integer(), nullable=False),
    sa.Column('in_stock', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_redis_id'), 'products', ['redis_id'], unique=True)
    op.create_foreign_key('fk_order_details_products', 'order_details', 'products', ['product_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_order_details_products', 'order_details', type_='foreignkey')
    op.drop_index(op.f('ix_products_redis_id'), table_name='products')
    op.drop_table('products')
    # ### end Alembic commands ###
