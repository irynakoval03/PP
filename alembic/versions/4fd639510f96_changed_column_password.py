"""changed column password

Revision ID: 4fd639510f96
Revises: 825e729bcc70
Create Date: 2021-11-18 13:53:23.816703

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '4fd639510f96'
down_revision = '825e729bcc70'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'password',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###