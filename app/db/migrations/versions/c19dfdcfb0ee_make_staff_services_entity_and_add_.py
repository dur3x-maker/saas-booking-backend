"""make staff_services entity and add bookings

Revision ID: c19dfdcfb0ee
Revises: fe98ab6a7125
Create Date: 2026-01-31 19:21:12.094327
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c19dfdcfb0ee"
down_revision: Union[str, Sequence[str], None] = "fe98ab6a7125"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------
    # NEW TABLES
    # ---------

    op.create_table(
        "time_off",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("staff_id", sa.Integer(), nullable=False),
        sa.Column("start_dt", sa.DateTime(), nullable=False),
        sa.Column("end_dt", sa.DateTime(), nullable=False),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["staff_id"], ["staff.id"]),
    )
    op.create_index(
        op.f("ix_time_off_staff_id"),
        "time_off",
        ["staff_id"],
    )

    op.create_table(
        "working_hours",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("staff_id", sa.Integer(), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("break_start", sa.Time(), nullable=True),
        sa.Column("break_end", sa.Time(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["staff_id"], ["staff.id"]),
        sa.UniqueConstraint("staff_id", "weekday", name="uq_staff_weekday"),
    )
    op.create_index(
        op.f("ix_working_hours_staff_id"),
        "working_hours",
        ["staff_id"],
    )

    # ------------------------
    # RECREATE staff_services
    # ------------------------

    # ⚠️ Осознанно дропаем таблицу (данных нет, проект в разработке)
    op.drop_table("staff_services")

    op.create_table(
        "staff_services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("staff_id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),

        sa.ForeignKeyConstraint(["staff_id"], ["staff.id"]),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),

        sa.UniqueConstraint(
            "staff_id",
            "service_id",
            name="uq_staff_service",
        ),
    )
    op.create_index(
        op.f("ix_staff_services_staff_id"),
        "staff_services",
        ["staff_id"],
    )
    op.create_index(
        op.f("ix_staff_services_service_id"),
        "staff_services",
        ["service_id"],
    )

    # --------
    # BOOKINGS
    # --------

    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("staff_id", sa.Integer(), nullable=False),
        sa.Column("staff_service_id", sa.Integer(), nullable=False),
        sa.Column("start_dt", sa.DateTime(), nullable=False),
        sa.Column("end_dt", sa.DateTime(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("duration_min", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "confirmed",
                "cancelled",
                "completed",
                "no_show",
                name="bookingstatus",
            ),
            nullable=False,
        ),
        sa.Column("customer_name", sa.String(), nullable=True),
        sa.Column("customer_phone", sa.String(), nullable=True),
        sa.Column("comment", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),

        sa.ForeignKeyConstraint(["staff_id"], ["staff.id"]),
        sa.ForeignKeyConstraint(["staff_service_id"], ["staff_services.id"]),
    )

    op.create_index(op.f("ix_bookings_staff_id"), "bookings", ["staff_id"])
    op.create_index(op.f("ix_bookings_staff_service_id"), "bookings", ["staff_service_id"])
    op.create_index(op.f("ix_bookings_start_dt"), "bookings", ["start_dt"])
    op.create_index(op.f("ix_bookings_end_dt"), "bookings", ["end_dt"])


def downgrade() -> None:
    # Для MVP downgrade держим минимальным
    op.drop_table("bookings")
    op.drop_table("staff_services")
    op.drop_table("working_hours")
    op.drop_table("time_off")
