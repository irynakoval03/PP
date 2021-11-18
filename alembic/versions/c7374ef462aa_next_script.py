"""Next script

Revision ID: c7374ef462aa
Revises: 1e9456722533
Create Date: 2021-11-16 09:57:47.704723

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c7374ef462aa'
down_revision = '1e9456722533'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'username',
               existing_type=mysql.VARCHAR(length=45),
               nullable=False)
    op.alter_column('user', 'firstName',
               existing_type=mysql.VARCHAR(length=45),
               nullable=False)
    op.alter_column('user', 'lastName',
               existing_type=mysql.VARCHAR(length=45),
               nullable=False)
    op.alter_column('user', 'email',
               existing_type=mysql.VARCHAR(length=45),
               nullable=False)
    op.alter_column('user', 'password',
               existing_type=mysql.VARCHAR(length=45),
               nullable=False)
    op.create_unique_constraint(None, 'user', ['username'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='unique')
    op.alter_column('user', 'password',
               existing_type=mysql.VARCHAR(length=45),
               nullable=True)
    op.alter_column('user', 'email',
               existing_type=mysql.VARCHAR(length=45),
               nullable=True)
    op.alter_column('user', 'lastName',
               existing_type=mysql.VARCHAR(length=45),
               nullable=True)
    op.alter_column('user', 'firstName',
               existing_type=mysql.VARCHAR(length=45),
               nullable=True)
    op.alter_column('user', 'username',
               existing_type=mysql.VARCHAR(length=45),
               nullable=True)
    # ### end Alembic commands ###
