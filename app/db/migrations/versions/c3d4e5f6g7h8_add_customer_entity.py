"""add customer entity and link to bookings

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-02-11 13:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6g7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    1. Создаём таблицу customers
    2. Backfill: для каждого уникального (business_id, customer_phone)
       в bookings создаём Customer
    3. Добавляем customer_id в bookings (nullable для SQLite)
    4. Backfill customer_id в bookings
    5. Удаляем customer_phone из bookings
    """
    conn = op.get_bind()

    # 1. Создаём таблицу customers
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('business_id', sa.Integer(), sa.ForeignKey('businesses.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.UniqueConstraint('business_id', 'phone', name='uq_customer_business_phone'),
    )
    op.create_index('ix_customers_business_id', 'customers', ['business_id'])
    op.create_index('ix_customers_phone', 'customers', ['phone'])
    op.create_index('ix_customers_business_phone', 'customers', ['business_id', 'phone'])

    # 2. Backfill: создаём Customer для каждого уникального (business_id, phone)
    #    из существующих bookings
    rows = conn.execute(sa.text(
        "SELECT DISTINCT business_id, customer_phone, customer_name "
        "FROM bookings "
        "WHERE customer_phone IS NOT NULL AND customer_phone != ''"
    )).fetchall()

    for row in rows:
        biz_id, phone, name = row[0], row[1], row[2] or "Unknown"
        conn.execute(sa.text(
            "INSERT INTO customers (business_id, name, phone, is_active, created_at) "
            "VALUES (:biz_id, :name, :phone, 1, datetime('now'))"
        ), {"biz_id": biz_id, "name": name, "phone": phone})

    # 3. Добавляем customer_id в bookings (nullable — SQLite ограничение)
    op.add_column('bookings', sa.Column(
        'customer_id', sa.Integer(), nullable=True,
    ))
    op.create_index('ix_bookings_customer_id', 'bookings', ['customer_id'])

    # 4. Backfill customer_id в bookings
    conn.execute(sa.text(
        "UPDATE bookings SET customer_id = ("
        "  SELECT c.id FROM customers c "
        "  WHERE c.business_id = bookings.business_id "
        "  AND c.phone = bookings.customer_phone"
        ") "
        "WHERE bookings.customer_phone IS NOT NULL AND bookings.customer_phone != ''"
    ))

    # 5. Для bookings без customer_phone — создаём placeholder customer
    orphan_bookings = conn.execute(sa.text(
        "SELECT DISTINCT business_id FROM bookings WHERE customer_id IS NULL"
    )).fetchall()

    for row in orphan_bookings:
        biz_id = row[0]
        # Проверяем, есть ли уже placeholder
        existing = conn.execute(sa.text(
            "SELECT id FROM customers "
            "WHERE business_id = :biz_id AND phone = 'unknown'"
        ), {"biz_id": biz_id}).fetchone()

        if existing is None:
            conn.execute(sa.text(
                "INSERT INTO customers (business_id, name, phone, is_active, created_at) "
                "VALUES (:biz_id, 'Unknown Customer', 'unknown', 1, datetime('now'))"
            ), {"biz_id": biz_id})

        conn.execute(sa.text(
            "UPDATE bookings SET customer_id = ("
            "  SELECT c.id FROM customers c "
            "  WHERE c.business_id = :biz_id AND c.phone = 'unknown'"
            ") "
            "WHERE bookings.business_id = :biz_id AND bookings.customer_id IS NULL"
        ), {"biz_id": biz_id})

    # 6. Удаляем customer_phone из bookings
    #    SQLite не поддерживает DROP COLUMN до 3.35.0,
    #    оставляем колонку но она больше не используется в ORM.
    #    При миграции на PostgreSQL — добавить op.drop_column('bookings', 'customer_phone')


def downgrade() -> None:
    """Откат: удаляем customer_id из bookings, удаляем таблицу customers."""
    op.drop_index('ix_bookings_customer_id', table_name='bookings')
    op.drop_column('bookings', 'customer_id')
    op.drop_index('ix_customers_business_phone', table_name='customers')
    op.drop_index('ix_customers_phone', table_name='customers')
    op.drop_index('ix_customers_business_id', table_name='customers')
    op.drop_table('customers')
