import json
import logging

from sqlalchemy.exc import IntegrityError, ProgrammingError

from src.domain.common.interfaces.cache import ICache
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

logger = logging.getLogger("main_logger")


async def clean_cache(
    cache: ICache, menu_id: str, submenu_id: str, dish_id: str | None = None
):
    await cache.delete("menus")
    await cache.delete("submenus")
    await cache.delete(f"submenus-{menu_id}")
    await cache.delete(f"dishes-{submenu_id}")
    await cache.delete(menu_id)
    await cache.delete(submenu_id)

    if dish_id:
        await cache.delete(dish_id)


class GetDishes(DishUseCase):
    async def __call__(self, menu_id: str, submenu_id: str):
        cache = await self.cache.get(f"dishes-{submenu_id}")

        if cache:
            return json.loads(cache)

        if await self.uow.menu_holder.submenu_repo.get_by_menu_id(menu_id, load=False):
            dishes = await self.uow.menu_holder.dish_repo.get_by_submenu(submenu_id)
            output_dishes = [dish.to_dto().dict() for dish in dishes]
            await self.cache.put(f"dishes-{submenu_id}", json.dumps(output_dishes))

            return output_dishes

        return []
        # raise SubMenuNotExists


class GetDish(DishUseCase):
    async def __call__(self, submenu_id: str, dish_id: str):
        cache = await self.cache.get(dish_id)
        if cache:
            return json.loads(cache)

        dish = await self.uow.menu_holder.dish_repo.get_by_submenu_and_id(
            submenu_id, dish_id
        )
        if dish:
            await self.cache.put(dish_id, json.dumps(dish.to_dto().dict()))
            return dish.to_dto()


class AddDish(DishUseCase):
    async def __call__(self, data: CreateDish) -> Dish:
        new_dish = self.uow.menu_holder.dish_repo.model(
            title=data.title,
            description=data.description,
            price=data.price,
            submenu_id=data.submenu_id,
        )

        await self.uow.menu_holder.dish_repo.save(new_dish)
        await self.uow.commit()
        await self.uow.menu_holder.dish_repo.refresh(new_dish)

        await clean_cache(self.cache, data.menu_id, data.submenu_id)

        await self.cache.put(str(new_dish.id), json.dumps(new_dish.to_dto().dict()))

        logger.info("Created new dish - %s", data.title)

        return new_dish.to_dto()


class DeleteDish(DishUseCase):
    async def __call__(self, menu_id: str, submenu_id: str, dish_id: str):
        dish_obj = await self.uow.menu_holder.dish_repo.get_by_submenu_and_id(
            submenu_id, dish_id
        )
        if dish_obj:
            await self.uow.menu_holder.dish_repo.delete(dish_obj)
            await self.uow.commit()

            await clean_cache(self.cache, menu_id, submenu_id, dish_id)

            logger.info("Dish was deleted - %s", dish_obj.title)
            return dish_obj


class PatchDish(DishUseCase):
    async def __call__(self, submenu_id: str, dish_id: str, data: dict) -> None:
        await self.uow.menu_holder.dish_repo.update_obj(dish_id, **data)
        await self.uow.commit()

        logger.info("Dish was updated - %s", dish_id)

        await self.cache.delete(dish_id)
        await self.cache.delete(f"dishes-{submenu_id}")


class DishService:
    def __init__(self, uow: IMenuUoW, cache: ICache):
        self.uow = uow
        self.cache = cache

    async def get_dishes(self, menu_id: str, submenu_id: str) -> list[Dish]:
        return await GetDishes(self.uow, self.cache)(menu_id, submenu_id)

    async def get_dish(self, submenu_id: str, dish_id: str) -> Dish:
        dish = await GetDish(self.uow, self.cache)(submenu_id, dish_id)
        if dish:
            return dish

        raise DishNotExists

    async def create_dish(self, data: CreateDish) -> Dish:
        try:
            if await self.uow.menu_holder.submenu_repo.get_by_menu_id(
                data.menu_id, load=False
            ):
                return await AddDish(self.uow, self.cache)(data)
            raise SubMenuNotExists
        except IntegrityError:
            raise DishAlreadyExists

    async def delete_dish(self, menu_id: str, submenu_id: str, dish_id: str) -> None:
        dish = await DeleteDish(self.uow, self.cache)(menu_id, submenu_id, dish_id)
        if dish:
            return

        raise DishNotExists

    async def update_dish(self, data: UpdateDish) -> Dish:
        try:
            await PatchDish(self.uow, self.cache)(
                data.submenu_id,
                data.dish_id,
                data.dict(
                    exclude_none=True, exclude={"menu_id", "submenu_id", "dish_id"}
                ),
            )
            updated_obj = await GetDish(self.uow, self.cache)(
                data.submenu_id, data.dish_id
            )
            if updated_obj:
                return updated_obj
            raise DishNotExists
        except ProgrammingError:
            raise DishDataEmpty
        except IntegrityError:
            raise DishAlreadyExists
