from src.domain.common.dto.base import DTO


class ReportDish(DTO):
    title: str
    description: str
    price: str


class ReportSubMenu(DTO):
    title: str
    description: str
    dishes: list[ReportDish]


class ReportMenu(DTO):
    title: str
    description: str
    submenus: list[ReportSubMenu]
