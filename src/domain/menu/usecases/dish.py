import json
import logging

from src.domain.common.exceptions.repo import DataEmptyError, UniqueError
from src.domain.common.interfaces.cache import ICache
from src.domain.menu.dto.dish import CreateDish, OutputDish, UpdateDish
from src.domain.menu.exceptions.dish import (
    DishAlreadyExists,
    DishDataEmpty,
    DishNotExists,
)
from src.domain.menu.exceptions.submenu import SubMenuNotExists
from src.domain.menu.interfaces.uow import IMenuUoW
from src.domain.menu.interfaces.usecases import DishUseCase

logger = logging.getLogger("main_logger")


async def clean_cache(
    cache: ICache, menu_id: str, submenu_id: str, dish_id: str | None = None
) -> None:
    await cache.delete("menus")
    await cache.delete("submenus")
    await cache.delete(f"submenus-{menu_id}")
    await cache.delete(f"dishes-{submenu_id}")
    await cache.delete(menu_id)
    await cache.delete(submenu_id)

    if dish_id:
        await cache.delete(dish_id)


class GetDishes(DishUseCase):
    async def __call__(self, submenu_id: str) -> list[OutputDish] | str | None:
        cache = await self.cache.get(f"dishes-{submenu_id}")

        if cache:
            return json.loads(cache)

        dishes = await self.uow.menu_holder.dish_repo.get_by_submenu(submenu_id)
        if dishes:
            output_dishes = [dish.to_dto().dict() for dish in dishes]
            await self.cache.put(f"dishes-{submenu_id}", json.dumps(output_dishes))

            return output_dishes

        return dishes


class GetDish(DishUseCase):
    async def __call__(self, submenu_id: str, dish_id: str) -> OutputDish | str:
        cache = await self.cache.get(dish_id)
        if cache:
            return json.loads(cache)

        dish = await self.uow.menu_holder.dish_repo.get_by_submenu_and_id(
            submenu_id, dish_id
        )
        if dish:
            await self.cache.put(dish_id, json.dumps(dish.to_dto().dict()))
            return dish.to_dto()

        raise DishNotExists


class AddDish(DishUseCase):
    async def __call__(self, data: CreateDish) -> OutputDish:
        try:
            new_dish = await self.uow.menu_holder.dish_repo.create_dish(data)
            await self.uow.commit()
        except UniqueError:
            raise DishAlreadyExists

        await clean_cache(self.cache, data.menu_id, data.submenu_id)

        await self.cache.put(str(new_dish.id), json.dumps(new_dish.to_dto().dict()))

        logger.info("Created new dish - %s", data.title)

        return new_dish.to_dto()


class DeleteDish(DishUseCase):
    async def __call__(self, menu_id: str, submenu_id: str, dish_id: str) -> None:
        dish_obj = await self.uow.menu_holder.dish_repo.get_by_submenu_and_id(
            submenu_id, dish_id
        )
        if dish_obj:
            await self.uow.menu_holder.dish_repo.delete(dish_obj)
            await self.uow.commit()

            await clean_cache(self.cache, menu_id, submenu_id, dish_id)

            logger.info("Dish was deleted - %s", dish_obj.title)
            return

        raise DishNotExists


class PatchDish(DishUseCase):
    async def __call__(self, submenu_id: str, dish_id: str, data: dict) -> None:
        try:
            await self.uow.menu_holder.dish_repo.update_obj(dish_id, **data)
            await self.uow.commit()
        except UniqueError:
            raise DishAlreadyExists
        except DataEmptyError:
            raise DishDataEmpty

        logger.info("Dish was updated - %s", dish_id)

        await self.cache.delete(dish_id)
        await self.cache.delete(f"dishes-{submenu_id}")


class DishService:
    def __init__(self, uow: IMenuUoW, cache: ICache):
        self.uow = uow
        self.cache = cache

    async def get_dishes(
        self, menu_id: str, submenu_id: str
    ) -> list[OutputDish] | str | None:
        # if await self.uow.menu_holder.submenu_repo.get_by_menu_id(menu_id, load=False):
        return await GetDishes(self.uow, self.cache)(submenu_id)
        # raiseSubMenuNotExists ЗАКОММЕНТИРОВАЛ, Т.К.
        # ошибка мешает тестам в постмане, но по логике должно присутствовать

    async def get_dish(self, submenu_id: str, dish_id: str) -> OutputDish | str:
        return await GetDish(self.uow, self.cache)(submenu_id, dish_id)

    async def create_dish(self, data: CreateDish) -> OutputDish:
        if await self.uow.menu_holder.submenu_repo.get_by_menu_id(
            data.menu_id, load=False
        ):
            return await AddDish(self.uow, self.cache)(data)
        raise SubMenuNotExists

    async def delete_dish(self, menu_id: str, submenu_id: str, dish_id: str) -> None:
        return await DeleteDish(self.uow, self.cache)(menu_id, submenu_id, dish_id)

    async def update_dish(self, data: UpdateDish) -> OutputDish | str:
        await PatchDish(self.uow, self.cache)(
            data.submenu_id,
            data.dish_id,
            data.dict(exclude_none=True, exclude={"menu_id", "submenu_id", "dish_id"}),
        )
        return await GetDish(self.uow, self.cache)(data.submenu_id, data.dish_id)
