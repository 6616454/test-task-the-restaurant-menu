import uuid

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.infrastructure.db.base import Base


class Dish(Base):
    __tablename__ = 'dish'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(32), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(String(19), nullable=False)

    submenu_id = Column(UUID, ForeignKey('submenu.id', ondelete='CASCADE'))

    submenu = relationship(
        'SubMenu', back_populates='dishes', single_parent=True)
