"""empty message

Revision ID: 53112323004a
Revises: 39cbede440f2
Create Date: 2023-12-16 03:11:12.663826

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '53112323004a'
down_revision = '39cbede440f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user2',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('password', sa.String(length=80), nullable=False),
    sa.Column('fname', sa.String(length=80), nullable=False),
    sa.Column('lname', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('role', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('invitation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user2.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('email')
        batch_op.drop_index('username')

    op.drop_table('user')
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_constraint('event_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user2', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('event_ibfk_1', 'user', ['user_id'], ['id'])

    op.create_table('user',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('username', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('password_hash', mysql.VARCHAR(length=120), nullable=False),
    sa.Column('fname', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('lname', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('role', mysql.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index('username', ['username'], unique=False)
        batch_op.create_index('email', ['email'], unique=False)

    op.drop_table('invitation')
    op.drop_table('user2')
    # ### end Alembic commands ###
