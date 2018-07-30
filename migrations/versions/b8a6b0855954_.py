"""empty message

Revision ID: b8a6b0855954
Revises: 419f5d371014
Create Date: 2018-07-29 16:11:24.895933

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8a6b0855954'
down_revision = '419f5d371014'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('guests', sa.Column('host_slackid', sa.String(length=100), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('guests', 'host_slackid')
    # ### end Alembic commands ###
