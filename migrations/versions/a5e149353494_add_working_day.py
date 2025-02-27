"""Add working day

Revision ID: a5e149353494
Revises: ccd9231dcfea
Create Date: 2024-08-13 13:11:11.484013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5e149353494'
down_revision = 'ccd9231dcfea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('work_sheet', schema=None) as batch_op:
        batch_op.add_column(sa.Column('WorkingDay', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('work_sheet', schema=None) as batch_op:
        batch_op.drop_column('WorkingDay')

    # ### end Alembic commands ###
