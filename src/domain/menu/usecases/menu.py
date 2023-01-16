import logging
from uuid import UUID

from sqlalchemy.exc import IntegrityError, ProgrammingError

from src.domain.menu.exceptions.menu import MenuAlreadyExists, MenuNotExists, MenuDataEmpty
from src.domain.menu.interfaces.uow import IMenuUoW
from src.domain.menu.interfaces.usecases import MenuUseCase
from src.domain.menu.schemas.menu import CreateMenu, OutputMenu, BaseMenu
from src.infrastructure.db.models.menu import Menu
from src.infrastructure.db.models.submenu import SubMenu

logger = logging.getLogger('main_logger')


class GetMenu(MenuUseCase):
    async def __call__(self, menu_id: str, load: bool = True) -> Menu:
        menu = await self.uow.menu_holder.menu_repo.get_by_id_all(menu_id, load)
        if menu:
            return menu
        raise MenuNotExists


class GetMenus(MenuUseCase):
    async def __call__(self) -> list[Menu]:
        return await self.uow.menu_holder.menu_repo.get_all()


class AddMenu(MenuUseCase):
    async def __call__(self, data: CreateMenu) -> Menu:
        menu = self.uow.menu_holder.menu_repo.model(
            title=data.title,
            description=data.description
        )

        await self.uow.menu_holder.menu_repo.save(menu)
        await self.uow.commit()
        await self.uow.menu_holder.menu_repo.refresh(menu)

        logger.info('New menu - %s', data.title)

        return menu


class DeleteMenu(MenuUseCase):
    async def __call__(self, menu_id: str):
        menu_obj = await self.uow.menu_holder.menu_repo.get_by_id(menu_id)
        if menu_obj:
            await self.uow.menu_holder.menu_repo.delete(menu_obj)
            await self.uow.commit()

            logger.info('Menu was deleted - %s', menu_obj.title)
            return

        raise MenuNotExists


class PatchMenu(MenuUseCase):
    async def __call__(self, menu_id: str, data: dict) -> None:
        await self.uow.menu_holder.menu_repo.update_obj(menu_id, **data)
        await self.uow.commit()


class MenuService:
    """Represents business logic for Menu entity."""

    @staticmethod
    async def _get_len(sub_menus: list[SubMenu], dishes: bool = False):
        if dishes:
            counter = 0

            for sub_menu in sub_menus:
                for dish in sub_menu.dishes:
                    counter += 1

            return counter

        return len(sub_menus)

    @staticmethod
    async def delete_menu(uow: IMenuUoW, menu_id: UUID) -> None:
        return await DeleteMenu(uow)(menu_id)

    async def _get_ready_info(self, obj: Menu) -> OutputMenu:
        return OutputMenu(
            id=obj.id,
            title=obj.title,
            description=obj.description,
            submenus_count=await self._get_len(obj.submenus),
            dishes_count=await self._get_len(obj.submenus, dishes=True)
        )

    @staticmethod
    async def create_menu(uow: IMenuUoW, data: CreateMenu) -> OutputMenu:
        try:
            return await AddMenu(uow)(data)
        except IntegrityError:
            await uow.rollback()

            raise MenuAlreadyExists

    async def update_menu(self, uow: IMenuUoW, menu_id: UUID, data: BaseMenu) -> OutputMenu:
        new_data = data.dict(exclude_unset=True)

        try:
            await PatchMenu(uow)(menu_id, new_data)
            updated_obj = await GetMenu(uow)(menu_id)
            return await self._get_ready_info(updated_obj)
        except ProgrammingError:
            raise MenuDataEmpty

    async def get_menus(self, uow: IMenuUoW) -> list[OutputMenu]:
        menus = await GetMenus(uow)()

        if menus:
            menus_info = [await self._get_ready_info(menu) for menu in menus]

            return menus_info

        return menus

    async def get_menu(self, uow: IMenuUoW, menu_id: UUID) -> OutputMenu:
        menu = await GetMenu(uow)(menu_id)
        return await self._get_ready_info(menu)
