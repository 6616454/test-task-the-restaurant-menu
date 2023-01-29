from src.domain.common.interfaces.cache import ICache
from src.domain.common.interfaces.uow import IBaseUoW
from src.infrastructure.db.uow import MenuHolder


class IMenuUoW(IBaseUoW):
    menu_holder: MenuHolder
    redis_repo: ICache
