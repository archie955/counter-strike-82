import re
from datetime import datetime

from sqlalchemy import (
    ARRAY,
    DECIMAL,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as sqlEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from database.database import Base
from models.enums import Majors, Nationality, Roles

nat = sqlEnum(Nationality, name="nat")
roles = sqlEnum(Roles, name="roles")
majors = sqlEnum(Majors, name="majors")


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_username", "username"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )

    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    best_lineup: Mapped["Lineup"] = relationship(
        "Lineup", back_populates="owner", cascade="all, delete-orphan"
    )

    @validates("email")
    def validate_email(self, key, value: str) -> str:
        if re.match(r"^\S+@\S+\.\S+$", value):
            return value
        else:
            raise ValueError("Invalid Email Format")

    @validates("username")
    def validate_username(self, key, value: str) -> str:
        if len(value) < 4:
            raise ValueError("Username is too short")
        return value


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    igl: Mapped[bool] = mapped_column(Boolean, nullable=False)

    awp: Mapped[bool] = mapped_column(Boolean, nullable=False)

    players: Mapped[list["Player"]] = relationship(
        "Player", back_populates="team", cascade="all, delete-orphan"
    )


class Player(Base):
    __tablename__ = "players"

    __table_args__ = (
        Index("ix_players_team_id", "team_id"),
        Index("ix_players_name", "name"),
        Index("ix_players_role", "role"),
        Index("ix_players_major", "major"),
        UniqueConstraint("name", "team_id", "major"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )

    nationality: Mapped[Nationality] = mapped_column(nat, nullable=False)

    major: Mapped[Majors] = mapped_column(majors, nullable=False)

    role: Mapped[list[Roles]] = mapped_column(ARRAY(roles), nullable=False)

    hltv: Mapped[float] = mapped_column(DECIMAL(3, 2), nullable=False)

    igl: Mapped[int] = mapped_column(
        Integer, CheckConstraint("igl > 0 AND igl < 5"), nullable=True
    )

    team: Mapped["Team"] = relationship("Team", back_populates="players")

    @validates("igl")
    def validate_igl(self, key, value: int) -> int:
        if not 0 < value < 5:
            raise ValueError(f"Invalid IGL score {value}")
        return value


class Lineup(Base):
    __tablename__ = "lineups"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    igl: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )

    awp: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )

    rifle_1: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )

    rifle_2: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )

    flex: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )

    score: Mapped[float] = mapped_column(DECIMAL(4, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    owner: Mapped["User"] = relationship("User", back_populates="best_lineup")
