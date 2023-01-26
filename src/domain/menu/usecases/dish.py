import logging

from sqlalchemy.exc import IntegrityError, ProgrammingError

from src.domain.menu.dto.dish import CreateDish, UpdateDish
from src.domain.menu.exceptions.dish import (
    DishAlreadyExists,
    DishDataEmpty,
    DishNotExists,
)
from src.domain.menu.exceptions.submenu import SubMenuNotExists
from src.domain.menu.interfaces.uow import IMenuUoW
from src.domain.menu.interfaces.usecases import DishUseCase
from src.infrastructure.db.models.dish import Dish

logger = logging.getLogger('main_logger')


class GetDishes(DishUseCase):
    async def __call__(self, menu_id: str, submenu_id: str):
        if await self.uow.menu_holder.submenu_repo.get_by_menu_id(menu_id, load=False):
            return await self.uow.menu_holder.dish_repo.get_by_submenu(submenu_id)

        return []
        # raise SubMenuNotExists


class GetDish(DishUseCase):
    async def __call__(self, submenu_id: str, dish_id: str):
        dish = await self.uow.menu_holder.dish_repo.get_by_submenu_and_id(submenu_id, dish_id)
        if dish:
            return dish

        raise DishNotExists


class AddDish(DishUseCase):
    async def __call__(self, data: CreateDish) -> Dish:
        new_dish = self.uow.menu_holder.dish_repo.model(
            title=data.title,
            description=data.description,
            price=data.price,
            submenu_id=data.submenu_id
        )

        await self.uow.menu_holder.dish_repo.save(new_dish)
        await self.uow.commit()
        await self.uow.menu_holder.dish_repo.refresh(new_dish)

        logger.info('Created new dish - %s', data.title)

        return new_dish


class DeleteDish(DishUseCase):
    async def __call__(self, submenu_id: str, dish_id: str):
        dish_obj = await self.uow.menu_holder.dish_repo.get_by_submenu_and_id(submenu_id, dish_id)
        if dish_obj:
            await self.uow.menu_holder.dish_repo.delete(dish_obj)
            await self.uow.commit()

            logger.info('Dish was deleted - %s', dish_obj.title)
            return

        raise DishNotExists


class PatchDish(DishUseCase):
    async def __call__(self, dish_id: str, data: dict) -> None:
        await self.uow.menu_holder.dish_repo.update_obj(dish_id, **data)
        await self.uow.commit()


class DishService:
    """Represents business logic for Dish entity."""

    @staticmethod
    async def get_dishes(uow: IMenuUoW, menu_id: str, submenu_id: str) -> list[Dish]:
        return await GetDishes(uow)(menu_id, submenu_id)

    @staticmethod
    async def get_dish(uow: IMenuUoW, submenu_id: str, dish_id: str) -> Dish:
        return await GetDish(uow)(submenu_id, dish_id)

    @staticmethod
    async def create_dish(uow: IMenuUoW, data: CreateDish) -> Dish:
        try:
            if await uow.menu_holder.submenu_repo.get_by_menu_id(data.menu_id, load=False):
                return await AddDish(uow)(data)
            raise SubMenuNotExists
        except IntegrityError:
            raise DishAlreadyExists

    @staticmethod
    async def delete_dish(uow: IMenuUoW, submenu_id: str, dish_id: str) -> None:
        return await DeleteDish(uow)(submenu_id, dish_id)

    @staticmethod
    async def update_dish(uow: IMenuUoW, data: UpdateDish) -> Dish:
        try:
            await PatchDish(uow)(data.dish_id, data.dict(
                exclude_none=True,
                exclude={'menu_id', 'submenu_id', 'dish_id'}
            ))
            updated_obj = await GetDish(uow)(data.submenu_id, data.dish_id)
            return updated_obj
        except ProgrammingError:
            raise DishDataEmpty
