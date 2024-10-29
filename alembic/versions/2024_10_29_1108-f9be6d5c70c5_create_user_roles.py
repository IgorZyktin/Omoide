"""create user roles

Revision ID: f9be6d5c70c5
Revises: 3cd33ce04e6c
Create Date: 2024-10-29 11:08:53.871977+03:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f9be6d5c70c5'
down_revision: Union[str, None] = '3cd33ce04e6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adding stuff."""
    op.create_table(
        'user_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('description', sa.VARCHAR(length=64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_user_roles_id'), 'user_roles', ['id'], unique=True
    )

    op.execute("INSERT INTO user_roles VALUES (0, 'user');")
    op.execute("INSERT INTO user_roles VALUES (1, 'anon');")
    op.execute("INSERT INTO user_roles VALUES (2, 'admin');")

    op.execute('GRANT SELECT ON user_roles TO omoide_app;')
    op.execute('GRANT SELECT ON user_roles TO omoide_worker;')
    op.execute('GRANT SELECT ON user_roles TO omoide_monitoring;')


def downgrade() -> None:
    """Removing stuff."""
    op.drop_index(op.f('ix_user_roles_id'), table_name='user_roles')
    op.drop_table('user_roles')
