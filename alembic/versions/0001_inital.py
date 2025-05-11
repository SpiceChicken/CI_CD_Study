"""create initial user + rbac schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-05-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 1) users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('username', sa.String(length=50), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(length=128), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    # 2) roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String(length=50), nullable=False, unique=True, index=True),
        sa.Column('description', sa.String(length=255), nullable=True),
    )

    # 3) permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column('description', sa.String(length=255), nullable=True),
    )

    # 4) association tables
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role_id', sa.Integer, sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    )
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer, sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('permission_id', sa.Integer, sa.ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    )

def downgrade():
    op.drop_table('role_permissions')
    op.drop_table('user_roles')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('users')