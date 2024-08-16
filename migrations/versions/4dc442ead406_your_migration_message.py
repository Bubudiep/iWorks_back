"""Your migration message

Revision ID: 4dc442ead406
Revises: 4e52352edebe
Create Date: 2024-08-16 17:46:32.395360

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4dc442ead406'
down_revision = '4e52352edebe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('work_sheet', schema=None) as batch_op:
        batch_op.add_column(sa.Column('JobsTitle', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('work_sheet', schema=None) as batch_op:
        batch_op.drop_column('JobsTitle')

    # ### end Alembic commands ###
