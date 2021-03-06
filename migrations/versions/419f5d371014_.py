"""empty message

Revision ID: 419f5d371014
Revises: 
Create Date: 2018-07-26 01:29:27.475777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '419f5d371014'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('guests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('guest_name', sa.String(length=100), nullable=False),
    sa.Column('host_name', sa.String(length=100), nullable=False),
    sa.Column('host_email', sa.String(length=100), nullable=False),
    sa.Column('purpose', sa.String(length=100), nullable=False),
    sa.Column('time_in', sa.DateTime(), nullable=False),
    sa.Column('time_out', sa.DateTime(), nullable=True),
    sa.Column('tag_no', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('guests')
    # ### end Alembic commands ###
