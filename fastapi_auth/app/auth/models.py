from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import Mapped, relationship

from fastapi_auth.app.database import Base


if TYPE_CHECKING:
    from app.group.models import Group


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    groups: Mapped[list["Group"]] = relationship(
        secondary="users_groups",
        back_populates="users",
    )
