from pydantic import UUID4, BaseModel

from src.domain.menu.dto.menu import BaseMenu


class BaseSubMenu(BaseMenu):
    pass


class OutputSubMenu(BaseModel):
    # Продублировал отдельно, чтобы подогнать под тесты

    id: UUID4
    title: str
    description: str
    dishes_count: int = 0

    class Config:
        orm_mode = True


class CreateSubMenu(BaseSubMenu):
    menu_id: str


class UpdateSubMenu(BaseSubMenu):
    menu_id: str
    submenu_id: str
    title: str = None
    description: str = None
