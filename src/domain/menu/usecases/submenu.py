import json
import logging

from src.domain.common.exceptions.repo import DataEmptyError, UniqueError
from src.domain.common.interfaces.cache import ICache
from src.domain.menu.dto.submenu import CreateSubMenu, OutputSubMenu, UpdateSubMenu
from src.domain.menu.exceptions.menu import MenuNotExists
from src.domain.menu.exceptions.submenu import (
    SubMenuAlreadyExists,
    SubMenuDataEmpty,
    SubMenuNotExists,
)
from src.domain.menu.interfaces.uow import IMenuUoW
from src.domain.menu.interfaces.usecases import SubMenuUseCase

logger = logging.getLogger("main_logger")


class GetSubMenu(SubMenuUseCase):
    async def __call__(  # type: ignore
        self, menu_id: str, submenu_id: str, load: bool
    ) -> OutputSubMenu | str:
        cache = await self.cache.get(submenu_id)
        if cache:
            return json.loads(cache)
        submenu = await self.uow.menu_holder.submenu_repo.get_by_menu_and_id(
            menu_id, submenu_id, load
        )
        if submenu:
            await self.cache.put(
                submenu_id, json.dumps(submenu.to_dto(len(submenu.dishes)).dict())
            )
            return submenu.to_dto(len(submenu.dishes))

        raise SubMenuNotExists


class GetSubMenus(SubMenuUseCase):
    async def __call__(self, menu_id: str) -> list[OutputSubMenu] | str | None:  # type: ignore
        cache = await self.cache.get(f"submenus-{menu_id}")
        if cache:
            return cache

        submenus = await self.uow.menu_holder.submenu_repo.get_by_menu_id(
            menu_id, load=True
        )
        if submenus:
            output_submenus = [
                submenu.to_dto(len(submenu.dishes)).dict() for submenu in submenus
            ]
            await self.cache.put(f"submenus-{menu_id}", json.dumps(output_submenus))
            return output_submenus

        return submenus


class AddSubMenu(SubMenuUseCase):
    async def __call__(self, data: CreateSubMenu) -> OutputSubMenu:
        try:
            new_submenu = await self.uow.menu_holder.submenu_repo.create_submenu(data)
            await self.uow.commit()
        except UniqueError:
            raise SubMenuNotExists

        await self.cache.delete(f"submenus-{data.menu_id}")
        await self.cache.delete(data.menu_id)
        await self.cache.delete("menus")

        await self.cache.put(
            str(new_submenu.id), json.dumps(new_submenu.to_dto().dict())
        )

        logger.info("New submenu - %s", data.title)

        return new_submenu.to_dto()


class DeleteSubMenu(SubMenuUseCase):
    async def __call__(self, menu_id: str, submenu_id: str) -> None:
        submenu_obj = await self.uow.menu_holder.submenu_repo.get_by_menu_and_id(
            menu_id, submenu_id, load=False
        )
        if submenu_obj:
            await self.uow.menu_holder.submenu_repo.delete(submenu_obj)
            await self.uow.commit()

            await self.cache.delete(submenu_id)
            await self.cache.delete(menu_id)
            await self.cache.delete(f"submenus-{menu_id}")
            await self.cache.delete("menus")

            logger.info("Submenu was deleted - %s", submenu_obj.title)

            return

        raise SubMenuNotExists


class PatchSubMenu(SubMenuUseCase):
    async def __call__(self, menu_id: str, submenu_id: str, data: dict) -> None:
        try:
            await self.uow.menu_holder.submenu_repo.update_obj(submenu_id, **data)
            await self.uow.commit()
        except UniqueError:
            raise SubMenuAlreadyExists
        except DataEmptyError:
            raise SubMenuDataEmpty

        logger.info("Submenu was updated - %s", submenu_id)

        await self.cache.delete(submenu_id)
        await self.cache.delete(f"submenus-{menu_id}")
        await self.cache.delete("menus")


class SubMenuService:
    """Represents business logic for Submenu entity."""

    def __init__(self, uow: IMenuUoW, cache: ICache):
        self.uow = uow
        self.cache = cache

    async def delete_submenu(self, menu_id: str, submenu_id: str) -> None:
        return await DeleteSubMenu(self.uow, self.cache)(menu_id, submenu_id)

    async def create_submenu(self, data: CreateSubMenu) -> OutputSubMenu:
        if await self.uow.menu_holder.menu_repo.get_by_id(data.menu_id):
            return await AddSubMenu(self.uow, self.cache)(data)
        raise MenuNotExists

    async def update_submenu(self, data: UpdateSubMenu) -> OutputSubMenu | str:
        await PatchSubMenu(self.uow, self.cache)(
            data.menu_id,
            data.submenu_id,
            data.dict(exclude_none=True, exclude={"submenu_id", "menu_id"}),
        )
        return await GetSubMenu(self.uow, self.cache)(
            data.menu_id, data.submenu_id, load=True
        )

    async def get_submenus(self, menu_id: str) -> list[OutputSubMenu] | str | None:
        if await self.uow.menu_holder.menu_repo.get_by_id(menu_id):
            return await GetSubMenus(self.uow, self.cache)(menu_id)

        raise MenuNotExists

    async def get_submenu(self, menu_id: str, submenu_id: str) -> OutputSubMenu | str:
        return await GetSubMenu(self.uow, self.cache)(menu_id, submenu_id, load=True)
