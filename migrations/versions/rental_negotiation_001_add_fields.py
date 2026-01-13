"""Add rental negotiation and comment fields to rentals table

Revision ID: rental_negotiation_001
Revises: add_profile_photo
Create Date: 2026-01-08 22:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'rental_negotiation_001'
down_revision = 'add_profile_photo'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to rentals table
    op.add_column('rentals', sa.Column('negotiated_price', sa.Float(), nullable=True))
    op.add_column('rentals', sa.Column('owner_response', sa.String(50), nullable=True))
    op.add_column('rentals', sa.Column('comment', sa.Text(), nullable=True))
    op.add_column('rentals', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Set default value for owner_response to 'pending' for existing records
    op.execute("UPDATE rentals SET owner_response = 'pending' WHERE owner_response IS NULL")
    op.execute("UPDATE rentals SET updated_at = created_at WHERE updated_at IS NULL")


def downgrade():
    # Remove columns from rentals table
    op.drop_column('rentals', 'updated_at')
    op.drop_column('rentals', 'comment')
    op.drop_column('rentals', 'owner_response')
    op.drop_column('rentals', 'negotiated_price')
