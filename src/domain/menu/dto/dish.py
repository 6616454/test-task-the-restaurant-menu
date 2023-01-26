from pydantic import UUID4, validator

from src.domain.common.dto.base import DTO
from src.domain.menu.dto.menu import BaseMenu


class BaseDish(BaseMenu):
    price: str

    @validator('price')
    def price_validator(cls, v):
        if v is None:
            return

        return f'{round(float(v), 2):.2f}'


class OutputDish(DTO):
    # Продублировал отдельно, чтобы подогнать под тесты
    id: UUID4
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
    title: str = None
    description: str = None
    price: str = None
