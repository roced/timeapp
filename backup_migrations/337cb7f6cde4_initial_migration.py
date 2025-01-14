"""Initial migration

Revision ID: 337cb7f6cde4
Revises: 
Create Date: 2024-01-14 17:34:38.786
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '337cb7f6cde4'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table first
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=128), nullable=True),
        sa.Column('role', sa.String(length=20), server_default='viewer'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_users'),
        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.UniqueConstraint('username', name='uq_users_username')
    )

    # Create events table
    op.create_table('events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('venue', sa.String(length=200), nullable=True),
        sa.Column('is_public', sa.Boolean(), server_default='0'),
        sa.Column('is_recurring', sa.Boolean(), server_default='0'),
        sa.Column('info_link', sa.String(length=500), nullable=True),
        sa.Column('tags', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('pending_promotion', sa.Boolean(), server_default='0'),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name='fk_events_owner'),
        sa.PrimaryKeyConstraint('id', name='pk_events')
    )

    # Create event_likes table
    op.create_table('event_likes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], name='fk_likes_event'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_likes_user'),
        sa.PrimaryKeyConstraint('id', name='pk_likes'),
        sa.UniqueConstraint('user_id', 'event_id', name='uq_user_event_like')
    )

    # Create event_attendance table
    op.create_table('event_attendance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], name='fk_attendance_event'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_attendance_user'),
        sa.PrimaryKeyConstraint('id', name='pk_attendance'),
        sa.UniqueConstraint('user_id', 'event_id', name='uq_user_event_attendance')
    )

    # Create wishlist_items table
    op.create_table('wishlist_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], name='fk_wishlist_event'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_wishlist_user'),
        sa.PrimaryKeyConstraint('id', name='pk_wishlist'),
        sa.UniqueConstraint('user_id', 'event_id', name='uq_user_event_wishlist')
    )

    # Create memos table
    op.create_table('memos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_memos_user'),
        sa.PrimaryKeyConstraint('id', name='pk_memos')
    )

def downgrade():
    op.drop_table('memos')
    op.drop_table('wishlist_items')
    op.drop_table('event_attendance')
    op.drop_table('event_likes')
    op.drop_table('events')
    op.drop_table('users')
