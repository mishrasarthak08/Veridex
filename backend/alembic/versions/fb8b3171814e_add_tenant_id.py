"""add_tenant_id

Revision ID: fb8b3171814e
Revises: 1d2894a46f12
Create Date: 2026-07-27 22:24:37.771149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb8b3171814e'
down_revision: Union[str, Sequence[str], None] = '1d2894a46f12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    tables = [
        "login_audit_logs",
        "chat_history",
        "connector_configs",
        "evaluation_runs",
        "oauth_accounts",
        "organizations",
        "permissions",
        "projects",
        "roles",
        "ai_logs",
        "users",
        "workspaces"
    ]
    for table in tables:
        op.add_column(table, sa.Column('tenant_id', sa.String(length=255), nullable=False, server_default='default_tenant'))
        op.create_index(op.f(f'ix_{table}_tenant_id'), table, ['tenant_id'], unique=False)

def downgrade() -> None:
    """Downgrade schema."""
    tables = [
        "login_audit_logs",
        "chat_history",
        "connector_configs",
        "evaluation_runs",
        "oauth_accounts",
        "organizations",
        "permissions",
        "projects",
        "roles",
        "ai_logs",
        "users",
        "workspaces"
    ]
    for table in tables:
        op.drop_index(op.f(f'ix_{table}_tenant_id'), table_name=table)
        op.drop_column(table, 'tenant_id')
