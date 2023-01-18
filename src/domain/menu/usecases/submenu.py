import logging
from uuid import UUID

from sqlalchemy.exc import IntegrityError, ProgrammingError

from src.domain.menu.exceptions.menu import MenuNotExists
from src.domain.menu.exceptions.submenu import SubMenuNotExists, SubMenuAlreadyExists, SubMenuDataEmpty
from src.domain.menu.interfaces.uow import IMenuUoW
from src.domain.menu.interfaces.usecases import SubMenuUseCase
from src.domain.menu.dto.submenu import CreateSubMenu, OutputSubMenu, BaseSubMenu, UpdateSubMenu
from src.infrastructure.db.models.dish import Dish
from src.infrastructure.db.models.submenu import SubMenu

logger = logging.getLogger('main_logger')


class GetSubMenu(SubMenuUseCase):
    async def __call__(self, menu_id: UUID, submenu_id: UUID) -> SubMenu:
        submenu = await self.uow.menu_holder.submenu_repo.get_by_menu_and_id(menu_id, submenu_id)
        if submenu:
            return submenu
        raise SubMenuNotExists


class GetSubMenus(SubMenuUseCase):
    async def __call__(self, menu_id: UUID) -> list[SubMenu]:
        if await self.uow.menu_holder.menu_repo.get_by_id(menu_id):
            return await self.uow.menu_holder.submenu_repo.get_by_menu_id(menu_id)


class AddSubMenu(SubMenuUseCase):
    async def __call__(self, data: CreateSubMenu) -> SubMenu:
        menu = self.uow.menu_holder.submenu_repo.model(
            title=data.title,
            description=data.description,
            menu_id=data.menu_id
        )

        await self.uow.menu_holder.submenu_repo.save(menu)
        await self.uow.commit()
        await self.uow.menu_holder.submenu_repo.refresh(menu)

        logger.info('New submenu - %s', data.title)

        return menu


class DeleteSubMenu(SubMenuUseCase):
    async def __call__(self, menu_id: str, submenu_id: str):
        submenu_obj = await self.uow.menu_holder.submenu_repo.get_by_menu_and_id(menu_id, submenu_id, load=False)
        if submenu_obj:
            await self.uow.menu_holder.submenu_repo.delete(submenu_obj)
            await self.uow.commit()

            logger.info('Submenu was deleted - %s', submenu_obj.title)
            return

        raise SubMenuNotExists


class PatchSubMenu(SubMenuUseCase):
    async def __call__(self, submenu_id: str, data: dict) -> None:
        await self.uow.menu_holder.submenu_repo.update_obj(submenu_id, **data)
        await self.uow.commit()


class SubMenuService:
    """Represents business logic for Submenu entity."""

    @staticmethod
    async def _get_len(dishes: list[Dish]):
        return len(dishes)

    @staticmethod
    async def delete_submenu(uow: IMenuUoW, menu_id: str, submenu_id: str) -> None:
        return await DeleteSubMenu(uow)(menu_id, submenu_id)

    @staticmethod
    async def create_submenu(uow: IMenuUoW, data: CreateSubMenu) -> OutputSubMenu:
        try:
            if await uow.menu_holder.menu_repo.get_by_id(data.menu_id):
                return await AddSubMenu(uow)(data)
            raise MenuNotExists
        except IntegrityError:
            await uow.rollback()

            raise SubMenuAlreadyExists

    async def _get_ready_info(self, obj: SubMenu) -> OutputSubMenu:
        return OutputSubMenu(
            id=obj.id,
            title=obj.title,
            description=obj.description,
            dishes_count=await self._get_len(obj.dishes),
        )

    async def update_submenu(self, uow: IMenuUoW, data: UpdateSubMenu) -> OutputSubMenu:
        try:
            await PatchSubMenu(uow)(data.submenu_id, data.dict(
                exclude_unset=True, exclude={'submenu_id', 'menu_id'}
            ))
            updated_obj = await GetSubMenu(uow)(data.menu_id, data.submenu_id)
            return await self._get_ready_info(updated_obj)
        except ProgrammingError:
            raise SubMenuDataEmpty

    async def get_submenus(self, uow: IMenuUoW, menu_id: str) -> list[OutputSubMenu]:
        submenus = await GetSubMenus(uow)(menu_id)

        if submenus:
            submenus_info = [await self._get_ready_info(submenu) for submenu in submenus]
            return submenus_info

        raise MenuNotExists

    async def get_submenu(self, uow: IMenuUoW, menu_id: str, submenu_id: str) -> OutputSubMenu:
        submenu = await GetSubMenu(uow)(menu_id, submenu_id)
        return await self._get_ready_info(submenu)
