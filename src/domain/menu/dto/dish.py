from pydantic import validator, UUID4

from src.domain.common.dto.base import DTO
from src.domain.menu.dto.menu import BaseMenu


class BaseDish(BaseMenu):
    price: str

    @validator('price')
    def price_validator(cls, v):
        return '{:.2f}'.format(round(float(v), 2))


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
    title: str = None
    description: str = None
    price: float = None
