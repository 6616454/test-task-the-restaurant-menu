from src.domain.common.dto.base import DTO
from src.domain.menu.dto.menu import BaseMenu


class BaseDish(BaseMenu):
    price: str


class OutputDish(DTO):
    # Продублировал отдельно, чтобы подогнать под тесты
    id: str
    title: str
    description: str
    price: str


class CreateDish(BaseDish):
    menu_id: str
    submenu_id: str


class UpdateDish(BaseDish):
    menu_id: str
    submenu_id: str
    dish_id: str
    title: str | None = None  # type: ignore
    description: str | None = None  # type: ignore
    price: str | None = None  # type: ignore
