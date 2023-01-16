import uuid

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.infrastructure.db.base import Base


class SubMenu(Base):
    __tablename__ = "submenu"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(32), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    menu_id = Column(UUID, ForeignKey("menu.id", ondelete='CASCADE'))

    menu = relationship("Menu", back_populates="submenus", single_parent=True)
    dishes = relationship("Dish", cascade="all, delete-orphan")
