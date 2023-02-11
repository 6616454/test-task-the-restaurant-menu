import json
import logging

from src.domain.common.exceptions.repo import DataEmptyError, UniqueError
from src.domain.common.interfaces.cache import ICache
from src.domain.menu.dto.menu import CreateMenu, OutputMenu, UpdateMenu
from src.domain.menu.exceptions.menu import (
    MenuAlreadyExists,
    MenuDataEmpty,
    MenuNotExists,
)
from src.domain.menu.interfaces.uow import IMenuUoW
from src.domain.menu.interfaces.usecases import MenuUseCase
from src.infrastructure.db.models.submenu import SubMenu

logger = logging.getLogger("main_logger")


async def get_len(sub_menus: list[SubMenu], dishes: bool = False) -> int:
    if dishes:
        counter = 0

        for sub_menu in sub_menus:
            for _ in sub_menu.dishes:
                counter += 1

        return counter

    return len(sub_menus)


class GetMenu(MenuUseCase):
    async def __call__(self, menu_id: str, load: bool) -> OutputMenu | str:
        cache = await self.cache.get(menu_id)
        if cache:
            return json.loads(cache)
        menu = await self.uow.menu_holder.menu_repo.get_by_id_all(menu_id, load)
        if menu:
            result_menu = menu.to_dto(
                await get_len(menu.submenus), await get_len(menu.submenus, dishes=True)
            ).dict()
            await self.cache.put(menu_id, json.dumps(result_menu))
            return result_menu

        raise MenuNotExists


class GetMenus(MenuUseCase):
    async def __call__(self) -> list[OutputMenu] | str:
        cache = await self.cache.get("menus")
        if cache:
            return json.loads(cache)
        menus = await self.uow.menu_holder.menu_repo.get_all()
        if menus:
            output_menus = [
                menu.to_dto(
                    await get_len(menu.submenus),
                    await get_len(menu.submenus, dishes=True),
                ).dict()
                for menu in menus
            ]
            await self.cache.put("menus", json.dumps(output_menus))
            return output_menus
        return menus


class AddMenu(MenuUseCase):
    async def __call__(self, data: CreateMenu) -> OutputMenu:
        try:
            new_menu = await self.uow.menu_holder.menu_repo.create_menu(data)
            await self.uow.commit()
        except UniqueError:
            raise MenuAlreadyExists

        await self.cache.put(str(new_menu.id), json.dumps(new_menu.to_dto().dict()))
        await self.cache.delete("menus")

        logger.info("New menu - %s", data.title)

        return new_menu.to_dto()


class DeleteMenu(MenuUseCase):
    async def __call__(self, menu_id: str) -> None:
        menu_obj = await self.uow.menu_holder.menu_repo.get_by_id(menu_id)
        if menu_obj:
            await self.uow.menu_holder.menu_repo.delete(menu_obj)
            await self.uow.commit()

            await self.cache.delete(str(menu_obj.id))
            await self.cache.delete("menus")

            logger.info("Menu was deleted - %s", menu_obj.title)
            return

        raise MenuNotExists


class PatchMenu(MenuUseCase):
    async def __call__(self, menu_id: str, data: dict) -> None:
        try:
            await self.uow.menu_holder.menu_repo.update_obj(menu_id, **data)
            await self.uow.commit()
        except UniqueError:
            raise MenuAlreadyExists
        except DataEmptyError:
            raise MenuDataEmpty

        logger.info("Menus was updated - %s", menu_id)

        await self.cache.delete(menu_id)
        await self.cache.delete("menus")


class MenuService:
    """Represents business logic for Menu entity."""

    def __init__(self, uow: IMenuUoW, cache: ICache):
        self.uow = uow
        self.cache = cache

    async def create_menu(self, data: CreateMenu) -> OutputMenu:
        return await AddMenu(self.uow, self.cache)(data)

    async def get_menus(self) -> list[OutputMenu] | str | None:
        return await GetMenus(self.uow, self.cache)()

    async def get_menu(self, menu_id: str) -> OutputMenu | str:
        return await GetMenu(self.uow, self.cache)(menu_id, load=True)

    async def delete_menu(self, menu_id: str) -> None:
        return await DeleteMenu(self.uow, self.cache)(menu_id)

    async def update_menu(self, data: UpdateMenu) -> OutputMenu | str:
        await PatchMenu(self.uow, self.cache)(
            data.menu_id, data.dict(exclude_none=True, exclude={"menu_id"})
        )
        return await GetMenu(self.uow, self.cache)(data.menu_id, load=True)
