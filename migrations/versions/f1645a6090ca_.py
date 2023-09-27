"""empty message

Revision ID: f1645a6090ca
Revises: 60a0ecc6ce37
Create Date: 2023-09-26 20:06:29.412713

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f1645a6090ca'
down_revision = '60a0ecc6ce37'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('website', sa.String(length=120), nullable=True))
        batch_op.drop_column('genre')

    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
        batch_op.add_column(sa.Column('website', sa.String(length=120), nullable=True))
        batch_op.drop_column('genre')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genre', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))
        batch_op.drop_column('website')
        batch_op.drop_column('genres')

    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genre', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))
        batch_op.drop_column('website')

    # ### end Alembic commands ###