"""auth: rewrite users, add business_users

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-02-11 13:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    SQLite limitations:
    - Cannot DROP COLUMN (role, business_id) on older SQLite.
    - Cannot ALTER COLUMN to add NOT NULL.
    We leave old columns in place; ORM no longer references them.

    Steps:
    1. Add created_at to users (nullable, backfill).
    2. Create business_users table.
    3. Backfill business_users from existing users.owner_id / business_id.
    """
    conn = op.get_bind()

    # 1. Add created_at to users if not exists
    # Check if column already exists (idempotent)
    inspector = sa.inspect(conn)
    user_cols = [c["name"] for c in inspector.get_columns("users")]

    if "created_at" not in user_cols:
        op.add_column("users", sa.Column(
            "created_at", sa.DateTime(), nullable=True,
        ))
        conn.execute(sa.text(
            "UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL"
        ))

    # 2. Create business_users table
    op.create_table(
        "business_users",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("businesses.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role", sa.String(), nullable=False, server_default="admin"),
    )
    op.create_index("ix_business_users_business_id", "business_users", ["business_id"])
    op.create_index("ix_business_users_user_id", "business_users", ["user_id"])

    # 3. Backfill: for each user with business_id, create owner mapping
    rows = conn.execute(sa.text(
        "SELECT id, business_id, role FROM users WHERE business_id IS NOT NULL"
    )).fetchall()

    for row in rows:
        user_id, business_id, role = row[0], row[1], row[2] or "owner"
        # Check if mapping already exists
        existing = conn.execute(sa.text(
            "SELECT 1 FROM business_users WHERE user_id = :uid AND business_id = :bid"
        ), {"uid": user_id, "bid": business_id}).fetchone()
        if not existing:
            conn.execute(sa.text(
                "INSERT INTO business_users (user_id, business_id, role) VALUES (:uid, :bid, :role)"
            ), {"uid": user_id, "bid": business_id, "role": role})

    # 4. Backfill: for each business with owner_id, ensure owner mapping
    biz_rows = conn.execute(sa.text(
        "SELECT id, owner_id FROM businesses WHERE owner_id IS NOT NULL"
    )).fetchall()

    for row in biz_rows:
        biz_id, owner_id = row[0], row[1]
        existing = conn.execute(sa.text(
            "SELECT 1 FROM business_users WHERE user_id = :uid AND business_id = :bid"
        ), {"uid": owner_id, "bid": biz_id}).fetchone()
        if not existing:
            conn.execute(sa.text(
                "INSERT INTO business_users (user_id, business_id, role) VALUES (:uid, :bid, 'owner')"
            ), {"uid": owner_id, "bid": biz_id})


def downgrade() -> None:
    op.drop_index("ix_business_users_user_id", table_name="business_users")
    op.drop_index("ix_business_users_business_id", table_name="business_users")
    op.drop_table("business_users")
