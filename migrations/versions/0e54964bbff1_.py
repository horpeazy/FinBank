"""empty message

Revision ID: 0e54964bbff1
Revises: 
Create Date: 2022-12-04 09:57:10.578175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e54964bbff1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('narration', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('fee', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_column('fee')
        batch_op.drop_column('narration')

    # ### end Alembic commands ###
