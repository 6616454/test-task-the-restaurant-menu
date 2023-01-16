import uuid

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.infrastructure.db.base import Base


class Menu(Base):
    __tablename__ = "menu"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(32), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    submenus = relationship("SubMenu", cascade="all, delete-orphan")
