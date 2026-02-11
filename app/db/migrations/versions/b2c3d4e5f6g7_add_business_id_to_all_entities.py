"""add business_id to staff, services, bookings, working_hours, time_off

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-11 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Multi-tenant migration:
    1. Создаём "Default Business" если businesses пуста
    2. Добавляем business_id (nullable) в staff, services, bookings,
       working_hours, time_off
    3. Backfill: назначаем всем записям default business_id
    4. Добавляем created_at в businesses (если нет)

    SQLite не поддерживает ALTER COLUMN SET NOT NULL,
    поэтому оставляем nullable=True и полагаемся на ORM-уровень NOT NULL.
    При миграции на PostgreSQL — добавить ALTER COLUMN SET NOT NULL.
    """
    conn = op.get_bind()

    # 1. Убедимся, что есть хотя бы один Business
    result = conn.execute(sa.text("SELECT id FROM businesses LIMIT 1"))
    row = result.fetchone()
    if row is None:
        conn.execute(sa.text(
            "INSERT INTO businesses (name, timezone, is_active) "
            "VALUES ('Default Business', 'UTC', 1)"
        ))
        result = conn.execute(sa.text("SELECT id FROM businesses LIMIT 1"))
        row = result.fetchone()

    default_business_id = row[0]

    # 2. Добавляем created_at в businesses (если нет)
    columns = [col['name'] for col in sa.inspect(conn).get_columns('businesses')]
    if 'created_at' not in columns:
        # SQLite не поддерживает non-constant defaults в ALTER TABLE,
        # поэтому добавляем nullable колонку и backfill-им
        op.add_column('businesses', sa.Column(
            'created_at', sa.DateTime(timezone=True), nullable=True,
        ))
        conn.execute(sa.text(
            "UPDATE businesses SET created_at = datetime('now') "
            "WHERE created_at IS NULL"
        ))

    # 3. Добавляем business_id в каждую таблицу + backfill + index
    tables = ['staff', 'services', 'bookings', 'working_hours', 'time_off']

    for table in tables:
        # SQLite не поддерживает ALTER TABLE ADD COLUMN с FK constraint,
        # поэтому добавляем просто Integer. FK обеспечивается на уровне ORM.
        op.add_column(table, sa.Column(
            'business_id', sa.Integer(), nullable=True,
        ))

        # Backfill существующих записей
        conn.execute(sa.text(
            f"UPDATE {table} SET business_id = :bid WHERE business_id IS NULL"
        ), {"bid": default_business_id})

        # Индекс
        op.create_index(
            f'ix_{table}_business_id',
            table,
            ['business_id'],
        )


def downgrade() -> None:
    """Удаляем business_id из всех таблиц."""
    tables = ['staff', 'services', 'bookings', 'working_hours', 'time_off']

    for table in tables:
        op.drop_index(f'ix_{table}_business_id', table_name=table)
        op.drop_column(table, 'business_id')
