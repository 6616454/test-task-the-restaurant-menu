import json
import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError, ProgrammingError

from src.domain.menu.dto.menu import CreateMenu, OutputMenu, UpdateMenu
from src.domain.menu.exceptions.menu import (
    MenuAlreadyExists,
    MenuDataEmpty,
    MenuNotExists,
)
from src.domain.menu.interfaces.uow import IMenuUoW
from src.domain.menu.interfaces.usecases import MenuUseCase
from src.infrastructure.db.models.menu import Menu
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
    async def __call__(self, menu_id: str, load: bool) -> str | OutputMenu:  # type: ignore
        cache = await self.uow.redis_repo.get(menu_id)
        if cache:
            return json.loads(cache)
        menu = await self.uow.menu_holder.menu_repo.get_by_id_all(menu_id, load)
        if menu:
            result_menu = menu.to_dto(
                await get_len(menu.submenus), await get_len(menu.submenus, dishes=True)
            ).dict()
            await self.uow.redis_repo.put(menu_id, json.dumps(result_menu))
            return result_menu


class GetMenus(MenuUseCase):
    async def __call__(self) -> list[OutputMenu] | str:
        cache = await self.uow.redis_repo.get("menus")
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
            await self.uow.redis_repo.put("menus", json.dumps(output_menus))
            return output_menus
        return menus


class AddMenu(MenuUseCase):
    async def __call__(self, data: CreateMenu) -> OutputMenu:
        menu = self.uow.menu_holder.menu_repo.model(
            title=data.title, description=data.description
        )

        await self.uow.menu_holder.menu_repo.save(menu)
        await self.uow.commit()
        await self.uow.menu_holder.menu_repo.refresh(menu)

        await self.uow.redis_repo.put(str(menu.id), json.dumps(menu.to_dto().dict()))
        await self.uow.redis_repo.delete("menus")

        logger.info("New menu - %s", data.title)

        return menu.to_dto()


class DeleteMenu(MenuUseCase):
    async def __call__(self, menu_id: str) -> Menu | None:  # type: ignore
        menu_obj = await self.uow.menu_holder.menu_repo.get_by_id(menu_id)
        if menu_obj:
            await self.uow.menu_holder.menu_repo.delete(menu_obj)
            await self.uow.commit()

            await self.uow.redis_repo.delete(str(menu_obj.id))
            await self.uow.redis_repo.delete("menus")

            logger.info("Menu was deleted - %s", menu_obj.title)
            return menu_obj


class PatchMenu(MenuUseCase):
    async def __call__(self, menu_id: str, data: dict) -> None:
        await self.uow.menu_holder.menu_repo.update_obj(menu_id, **data)
        await self.uow.commit()

        await self.uow.redis_repo.delete(menu_id)
        await self.uow.redis_repo.delete("menus")


@dataclass
class MenuService:
    """Represents business logic for Menu entity."""

    @staticmethod
    async def create_menu(uow: IMenuUoW, data: CreateMenu) -> OutputMenu:
        try:
            return await AddMenu(uow)(data)
        except IntegrityError:
            await uow.rollback()
        raise MenuAlreadyExists

    @staticmethod
    async def get_menus(uow: IMenuUoW) -> list[OutputMenu] | str | None:
        return await GetMenus(uow)()

    @staticmethod
    async def get_menu(uow: IMenuUoW, menu_id: str) -> OutputMenu | str | MenuNotExists:
        menu = await GetMenu(uow)(menu_id, load=True)
        if menu:
            return menu
        raise MenuNotExists

    @staticmethod
    async def delete_menu(uow: IMenuUoW, menu_id: str) -> None:
        menu = await DeleteMenu(uow)(menu_id)
        if menu:
            return
        raise MenuNotExists

    @staticmethod
    async def update_menu(
        uow: IMenuUoW, data: UpdateMenu
    ) -> OutputMenu | str | MenuNotExists | MenuDataEmpty:
        try:
            await PatchMenu(uow)(
                data.menu_id, data.dict(exclude_none=True, exclude={"menu_id"})
            )
            menu = await GetMenu(uow)(data.menu_id, load=True)
            if menu:
                return menu

            raise MenuNotExists
        except ProgrammingError:
            raise MenuDataEmpty
