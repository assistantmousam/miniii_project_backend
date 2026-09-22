"""fix question qotd fields

Revision ID: 2f667ccd8863
Revises: 174fb45060bb
Create Date: 2026-09-22 08:20:50.557776
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2f667ccd8863"
down_revision: Union[str, Sequence[str], None] = "174fb45060bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Add QOTD eligibility column.
    #
    # server_default=True allows PostgreSQL to populate
    # existing rows instead of inserting NULL.
    # ---------------------------------------------------------
    op.add_column(
        "questions",
        sa.Column(
            "is_qotd_eligible",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    # Remove the database-level default after existing rows
    # have been populated.
    op.alter_column(
        "questions",
        "is_qotd_eligible",
        server_default=None,
    )

    # ---------------------------------------------------------
    # Indexes
    # ---------------------------------------------------------
    op.create_index(
        "ix_questions_is_qotd_eligible",
        "questions",
        ["is_qotd_eligible"],
        unique=False,
    )

    op.create_index(
        "ix_questions_used_date",
        "questions",
        ["used_date"],
        unique=False,
    )

    # ---------------------------------------------------------
    # Streak -> User foreign key
    # ---------------------------------------------------------
    op.create_foreign_key(
        "fk_streaks_user_id_users",
        "streaks",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # Remove foreign key
    op.drop_constraint(
        "fk_streaks_user_id_users",
        "streaks",
        type_="foreignkey",
    )

    # Remove indexes
    op.drop_index(
        "ix_questions_used_date",
        table_name="questions",
    )

    op.drop_index(
        "ix_questions_is_qotd_eligible",
        table_name="questions",
    )

    # Remove column
    op.drop_column(
        "questions",
        "is_qotd_eligible",
    )