"""Add profile photo URL to users table

Revision ID: add_profile_photo
Revises: e1cc204f95b4
Create Date: 2026-01-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_profile_photo'
down_revision = 'e1cc204f95b4'
branch_labels = None
depends_on = None


def upgrade():
    # Add profile_photo_url column to users table
    op.add_column('users', sa.Column('profile_photo_url', sa.String(255), nullable=True))


def downgrade():
    # Remove profile_photo_url column from users table
    op.drop_column('users', 'profile_photo_url')
