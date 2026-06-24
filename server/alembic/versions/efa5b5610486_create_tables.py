"""create tables

Revision ID: efa5b5610486
Revises:
Create Date: 2026-06-23 17:33:10.488419

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from models.models import majors, nat, roles

# revision identifiers, used by Alembic.
revision: str = "efa5b5610486"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer,
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(100),
            sa.CheckConstraint("REGEXP_LIKE(email, '^\S+@\S+\.\S+$')"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "username",
            sa.String(100),
            sa.CheckConstraint("LENGTH(username) > 4"),
            unique=True,
            nullable=False,
        ),
        sa.Column(
            "hashed_password",
            sa.String(200),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "teams",
        sa.Column(
            "id",
            sa.Integer,
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(100),
            nullable=False,
        ),
        sa.Column("igl", sa.Boolean, nullable=False),
        sa.Column("awp", sa.Boolean, nullable=False),
    )

    op.create_table(
        "players",
        sa.Column(
            "id",
            sa.Integer,
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "team_id",
            sa.Integer,
            sa.ForeignKey("teams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "nationality",
            nat,
            nullable=False,
        ),
        sa.Column(
            "major",
            majors,
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.ARRAY(roles),
            nullable=False,
        ),
        sa.Column(
            "hltv",
            sa.DECIMAL(3, 2),
            nullable=False,
        ),
        sa.Column(
            "igl", sa.Integer, sa.CheckConstraint("igl > 0 AND igl < 5"), nullable=True
        ),
    )

    op.create_index("ix_players_team_id", "players", ["team"])
    op.create_index("ix_players_name", "players", ["name"])
    op.create_index("ix_players_role", "players", ["role"])
    op.create_index("ix_players_major", "players", ["major"])
    op.create_unique_constraint(
        "uq_players_name_team_id_major", "players", ["name", "team", "major"]
    )

    op.create_table(
        "lineups",
        sa.Column(
            "id",
            sa.Integer,
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "igl",
            sa.Integer,
            sa.ForeignKey("players.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "awp",
            sa.Integer,
            sa.ForeignKey("players.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "rifle_1",
            sa.Integer,
            sa.ForeignKey("players.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "rifle_2",
            sa.Integer,
            sa.ForeignKey("players.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "flex",
            sa.Integer,
            sa.ForeignKey("players.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("score", sa.DECIMAL(4, 2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_lineups_user_id", "lineups", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_lineups_user_id", "lineups")
    op.drop_table("lineups")

    op.drop_constraint("uq_players_name_team_id_major", "players")
    op.drop_index("ix_players_team_id", "players")
    op.drop_index("ix_players_name", "players")
    op.drop_index("ix_players_role", "players")
    op.drop_index("ix_players_major", "players")
    op.drop_table("players")

    op.drop_index("ix_users_email", "users")
    op.drop_index("ix_users_username", "users")
    op.drop_table("users")
