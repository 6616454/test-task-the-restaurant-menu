import uuid

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.domain.menu.dto.submenu import OutputSubMenu
from src.infrastructure.db.base import Base


class SubMenu(Base):
    __tablename__ = "submenu"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(32), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    menu_id = Column(UUID, ForeignKey("menu.id", ondelete="CASCADE"))

    menu = relationship("Menu", back_populates="submenus", single_parent=True)
    dishes = relationship("Dish", cascade="all, delete-orphan")

    def to_dto(self, dishes_count: int = 0) -> OutputSubMenu:
        return OutputSubMenu(
            id=str(self.id),
            title=self.title,
            description=self.description,
            dishes_count=dishes_count,
        )
