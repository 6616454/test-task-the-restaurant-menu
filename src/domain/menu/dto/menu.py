from src.domain.common.dto.base import DTO


class BaseMenu(DTO):
    title: str
    description: str


class OutputMenu(DTO):
    # Продублировал отдельно, чтобы подогнать под тесты

    id: str
    title: str
    description: str
    submenus_count: int = 0
    dishes_count: int = 0


class CreateMenu(BaseMenu):
    pass


class UpdateMenu(BaseMenu):
    menu_id: str
    title: str | None = None  # type: ignore
    description: str | None = None  # type: ignore
