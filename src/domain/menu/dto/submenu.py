from src.domain.common.dto.base import DTO
from src.domain.menu.dto.menu import BaseMenu


class BaseSubMenu(BaseMenu):
    pass


class OutputSubMenu(DTO):
    # Продублировал отдельно, чтобы подогнать под тесты

    id: str
    title: str
    description: str
    dishes_count: int = 0


class CreateSubMenu(BaseSubMenu):
    menu_id: str


class UpdateSubMenu(BaseSubMenu):
    menu_id: str
    submenu_id: str
    title: str = None
    description: str = None
