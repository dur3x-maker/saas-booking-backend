"""booking: status enum HOLD/CONFIRMED/CANCELLED/EXPIRED, add expires_at, composite index

Revision ID: a1b2c3d4e5f6
Revises: ed0a0dd18762
Create Date: 2026-02-11 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'ed0a0dd18762'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Добавляем колонку expires_at
    op.add_column(
        'bookings',
        sa.Column('expires_at', sa.DateTime(), nullable=True),
    )

    # 2. Обновляем существующие статусы на новые значения enum
    #    SQLite хранит enum как VARCHAR, поэтому просто обновляем значения
    op.execute("UPDATE bookings SET status = 'confirmed' WHERE status = 'confirmed'")
    op.execute("UPDATE bookings SET status = 'cancelled' WHERE status = 'cancelled'")
    op.execute("UPDATE bookings SET status = 'hold' WHERE status = 'pending'")
    op.execute("UPDATE bookings SET status = 'expired' WHERE status = 'completed'")
    op.execute("UPDATE bookings SET status = 'cancelled' WHERE status = 'no_show'")

    # 3. Составной индекс для быстрого поиска пересечений
    op.create_index(
        'ix_bookings_staff_overlap',
        'bookings',
        ['staff_id', 'start_at', 'end_at', 'status'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_bookings_staff_overlap', table_name='bookings')

    # Откатываем статусы
    op.execute("UPDATE bookings SET status = 'pending' WHERE status = 'hold'")
    op.execute("UPDATE bookings SET status = 'completed' WHERE status = 'expired'")

    op.drop_column('bookings', 'expires_at')
