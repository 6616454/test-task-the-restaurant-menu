from src.domain.common.interfaces.uow import IBaseUoW
from src.infrastructure.db.uow import MenuHolder


class IMenuUoW(IBaseUoW):
    menu_holder: MenuHolder
