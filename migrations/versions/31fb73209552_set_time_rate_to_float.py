"""set time rate to float

Revision ID: 31fb73209552
Revises: 9455d5c6d100
Create Date: 2024-09-07 14:41:25.137501

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31fb73209552'
down_revision = '9455d5c6d100'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('work_record', schema=None) as batch_op:
        batch_op.add_column(sa.Column('leaveType', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('work_record', schema=None) as batch_op:
        batch_op.drop_column('leaveType')

    # ### end Alembic commands ###
