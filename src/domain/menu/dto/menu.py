from pydantic import UUID4

from src.domain.common.dto.base import DTO


class BaseMenu(DTO):
    title: str
    description: str


class OutputMenu(DTO):
    # Продублировал отдельно, чтобы подогнать под тесты

    id: UUID4
    title: str
    description: str
    submenus_count: int = 0
    dishes_count: int = 0


class CreateMenu(BaseMenu):
    pass


class UpdateMenu(BaseMenu):
    menu_id: str
    title: str | None = None
    description: str | None = None
