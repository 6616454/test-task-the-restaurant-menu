import json
import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError, ProgrammingError

from src.domain.menu.dto.submenu import CreateSubMenu, OutputSubMenu, UpdateSubMenu
from src.domain.menu.exceptions.menu import MenuNotExists
from src.domain.menu.exceptions.submenu import (
    SubMenuAlreadyExists,
    SubMenuDataEmpty,
    SubMenuNotExists,
)
from src.domain.menu.interfaces.uow import IMenuUoW
from src.domain.menu.interfaces.usecases import SubMenuUseCase
from src.infrastructure.db.models.submenu import SubMenu
from src.infrastructure.db.uow import SQLAlchemyUoW

logger = logging.getLogger("main_logger")


class GetSubMenu(SubMenuUseCase):
    async def __call__(  # type: ignore
        self, menu_id: str, submenu_id: str, load: bool
    ) -> OutputSubMenu | str:
        cache = await self.uow.redis_repo.get(submenu_id)
        if cache:
            return json.loads(cache)
        submenu = await self.uow.menu_holder.submenu_repo.get_by_menu_and_id(
            menu_id, submenu_id, load
        )
        if submenu:
            await self.uow.redis_repo.put(
                submenu_id, json.dumps(submenu.to_dto(len(submenu.dishes)).dict())
            )
            return submenu.to_dto(len(submenu.dishes))


class GetSubMenus(SubMenuUseCase):
    async def __call__(self, menu_id: str) -> list[OutputSubMenu] | str | None:  # type: ignore
        if await self.uow.menu_holder.menu_repo.get_by_id(menu_id):
            cache = await self.uow.redis_repo.get(f"submenus-{menu_id}")
            if cache:
                return cache

            submenus = await self.uow.menu_holder.submenu_repo.get_by_menu_id(
                menu_id, load=True
            )
            if submenus:
                output_submenus = [
                    submenu.to_dto(len(submenu.dishes)).dict() for submenu in submenus
                ]
                await self.uow.redis_repo.put(
                    f"submenus-{menu_id}", json.dumps(output_submenus)
                )
                return output_submenus

            return submenus


class AddSubMenu(SubMenuUseCase):
    async def __call__(self, data: CreateSubMenu) -> OutputSubMenu:
        submenu = self.uow.menu_holder.submenu_repo.model(
            title=data.title, description=data.description, menu_id=data.menu_id
        )

        await self.uow.menu_holder.submenu_repo.save(submenu)
        await self.uow.commit()
        await self.uow.menu_holder.submenu_repo.refresh(submenu)

        await self.uow.redis_repo.delete(f"submenus-{data.menu_id}")
        await self.uow.redis_repo.delete(data.menu_id)
        await self.uow.redis_repo.delete("menus")

        await self.uow.redis_repo.put(
            str(submenu.id), json.dumps(submenu.to_dto().dict())
        )

        logger.info("New submenu - %s", data.title)

        return submenu.to_dto()


class DeleteSubMenu(SubMenuUseCase):
    async def __call__(self, menu_id: str, submenu_id: str) -> SubMenu:  # type: ignore
        submenu_obj = await self.uow.menu_holder.submenu_repo.get_by_menu_and_id(
            menu_id, submenu_id, load=False
        )
        if submenu_obj:
            await self.uow.menu_holder.submenu_repo.delete(submenu_obj)
            await self.uow.commit()

            await self.uow.redis_repo.delete(submenu_id)
            await self.uow.redis_repo.delete(menu_id)
            await self.uow.redis_repo.delete(f"submenus-{menu_id}")
            await self.uow.redis_repo.delete("menus")
            logger.info("Submenu was deleted - %s", submenu_obj.title)

            return submenu_obj


class PatchSubMenu(SubMenuUseCase):
    async def __call__(self, menu_id: str, submenu_id: str, data: dict) -> None:
        await self.uow.menu_holder.submenu_repo.update_obj(submenu_id, **data)
        await self.uow.commit()

        await self.uow.redis_repo.delete(submenu_id)
        await self.uow.redis_repo.delete(f"submenus-{menu_id}")
        await self.uow.redis_repo.delete("menus")


@dataclass
class SubMenuService:
    """Represents business logic for Submenu entity."""

    @staticmethod
    async def delete_submenu(uow: IMenuUoW, menu_id: str, submenu_id: str) -> None:
        submenu = await DeleteSubMenu(uow)(menu_id, submenu_id)
        if submenu:
            return

        raise SubMenuNotExists

    @staticmethod
    async def create_submenu(uow: IMenuUoW, data: CreateSubMenu) -> OutputSubMenu:
        try:
            if await uow.menu_holder.menu_repo.get_by_id(data.menu_id):
                return await AddSubMenu(uow)(data)
            raise MenuNotExists
        except IntegrityError:
            await uow.rollback()

            raise SubMenuAlreadyExists

    @staticmethod
    async def update_submenu(uow: IMenuUoW, data: UpdateSubMenu) -> OutputSubMenu | str:
        try:
            await PatchSubMenu(uow)(
                data.menu_id,
                data.submenu_id,
                data.dict(exclude_none=True, exclude={"submenu_id", "menu_id"}),
            )
            new_submenu = await GetSubMenu(uow)(
                data.menu_id, data.submenu_id, load=True
            )
            if new_submenu:
                return new_submenu
            raise SubMenuNotExists
        except ProgrammingError:
            raise SubMenuDataEmpty

    @staticmethod
    async def get_submenus(
        uow: SQLAlchemyUoW | IMenuUoW, menu_id: str
    ) -> list[OutputSubMenu] | str | MenuNotExists:
        submenus = await GetSubMenus(uow)(menu_id)  # type: ignore

        if submenus is None and not isinstance(submenus, list):
            raise MenuNotExists

        return submenus

    @staticmethod
    async def get_submenu(
        uow: IMenuUoW, menu_id: str, submenu_id: str
    ) -> OutputSubMenu | str:
        submenu = await GetSubMenu(uow)(menu_id, submenu_id, load=True)
        if submenu:
            return submenu

        raise SubMenuNotExists
