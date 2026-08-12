"""seed default roles

Revision ID: 0c34e4998a38
Revises: fb8b3171814e
Create Date: 2026-07-30 20:41:59.414543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c34e4998a38'
down_revision: Union[str, Sequence[str], None] = 'fb8b3171814e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Seed Permissions
    op.execute("""
    INSERT INTO permissions (id, name, resource, action, created_at, updated_at) VALUES 
    (gen_random_uuid(), 'Manage Projects', 'project', '*', NOW(), NOW()),
    (gen_random_uuid(), 'Read Projects', 'project', 'read', NOW(), NOW()),
    (gen_random_uuid(), 'Manage Workspaces', 'workspace', '*', NOW(), NOW()),
    (gen_random_uuid(), 'Read Workspaces', 'workspace', 'read', NOW(), NOW()),
    (gen_random_uuid(), 'Manage Billing', 'billing', '*', NOW(), NOW()),
    (gen_random_uuid(), 'Manage Roles', 'roles', '*', NOW(), NOW()),
    (gen_random_uuid(), 'All Access', '*', '*', NOW(), NOW())
    ON CONFLICT DO NOTHING;
    """)

    # Seed Roles
    op.execute("""
    INSERT INTO roles (id, name, description, created_at, updated_at) VALUES 
    (gen_random_uuid(), 'owner', 'Full administrative access including billing and governance', NOW(), NOW()),
    (gen_random_uuid(), 'admin', 'Administrative access to workspaces and projects', NOW(), NOW()),
    (gen_random_uuid(), 'member', 'Standard access to collaborate on projects', NOW(), NOW()),
    (gen_random_uuid(), 'viewer', 'Read-only access', NOW(), NOW())
    ON CONFLICT (name) DO NOTHING;
    """)

    # Link Roles to Permissions
    # Owner gets All Access
    op.execute("""
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT r.id, p.id FROM roles r, permissions p 
    WHERE r.name = 'owner' AND p.name = 'All Access'
    ON CONFLICT DO NOTHING;
    """)
    
    # Admin gets Manage Projects, Manage Workspaces
    op.execute("""
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT r.id, p.id FROM roles r, permissions p 
    WHERE r.name = 'admin' AND p.name IN ('Manage Projects', 'Manage Workspaces')
    ON CONFLICT DO NOTHING;
    """)
    
    # Member gets Manage Projects, Read Workspaces
    op.execute("""
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT r.id, p.id FROM roles r, permissions p 
    WHERE r.name = 'member' AND p.name IN ('Manage Projects', 'Read Workspaces')
    ON CONFLICT DO NOTHING;
    """)

    # Viewer gets Read Projects, Read Workspaces
    op.execute("""
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT r.id, p.id FROM roles r, permissions p 
    WHERE r.name = 'viewer' AND p.name IN ('Read Projects', 'Read Workspaces')
    ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM role_permissions;")
    op.execute("DELETE FROM roles;")
    op.execute("DELETE FROM permissions;")
