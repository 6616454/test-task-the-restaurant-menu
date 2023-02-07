from src.domain.common.interfaces.uow import IBaseUoW
from src.infrastructure.db.uow import MenuHolder


class IReportUoW(IBaseUoW):
    menu_holder: MenuHolder
