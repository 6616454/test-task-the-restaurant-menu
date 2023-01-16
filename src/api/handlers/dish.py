from typing import Union, Optional

from fastapi import Depends, Response, status, APIRouter
from pydantic import UUID4

from src.api.di import uow_provider, dish_service_stub
from src.api.handlers.responses.dish import DishDeleteResponse
from src.api.handlers.responses.exceptions import DishNotFoundError, DishAlreadyExistsError, SubMenuNotFoundError, \
    DishEmptyRequestBodyError
from src.domain.menu.exceptions.dish import DishNotExists, DishAlreadyExists, DishDataEmpty
from src.domain.menu.exceptions.submenu import SubMenuNotExists
from src.domain.menu.schemas.dish import CreateDish, OutputDish, UpdateDish
from src.domain.menu.usecases.dish import DishService
from src.infrastructure.db.repositories.holder import SQLAlchemyUoW

router = APIRouter(
    prefix='/api/v1/menus',
    tags=['dishes']
)


# Dish Routes

@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': SubMenuNotFoundError
        }
    }
)
async def get_dishes(
        menu_id: UUID4,
        submenu_id: UUID4,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        dish_service: DishService = Depends(dish_service_stub)
) -> Optional[list[OutputDish]]:
    return await dish_service.get_dishes(uow, str(menu_id), str(submenu_id))


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': DishNotFoundError
        }
    }
)
async def get_dish(
        menu_id: UUID4,
        submenu_id: UUID4,
        dish_id: UUID4,
        response: Response,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        dish_service: DishService = Depends(dish_service_stub)
) -> Union[OutputDish, DishNotFoundError]:
    try:
        return await dish_service.get_dish(uow, str(submenu_id), str(dish_id))
    except DishNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DishNotFoundError()


@router.post(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': DishAlreadyExistsError
        },
        status.HTTP_404_NOT_FOUND: {
            'model': SubMenuNotFoundError
        }
    },
    status_code=status.HTTP_201_CREATED
)
async def create_dish(
        menu_id: UUID4,
        submenu_id: UUID4,
        response: Response,
        dish_data: CreateDish,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        dish_service: DishService = Depends(dish_service_stub)
) -> Union[OutputDish, SubMenuNotFoundError, DishAlreadyExistsError]:
    try:
        return await dish_service.create_dish(uow, str(menu_id), str(submenu_id), dish_data)
    except SubMenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return SubMenuNotFoundError()
    except DishAlreadyExists:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return DishAlreadyExistsError()


@router.delete(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    responses={
        status.HTTP_200_OK: {
            'model': DishDeleteResponse
        },
        status.HTTP_404_NOT_FOUND: {
            'model': DishNotFoundError
        }
    }
)
async def delete_dish(
        menu_id: UUID4,
        submenu_id: UUID4,
        dish_id: UUID4,
        response: Response,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        dish_service: DishService = Depends(dish_service_stub)
):
    try:
        await dish_service.delete_dish(uow, str(submenu_id), str(dish_id))
        return DishDeleteResponse()
    except DishNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DishNotFoundError()


@router.patch(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': DishNotFoundError
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': DishEmptyRequestBodyError
        }
    }
)
async def update_submenu(
        menu_id: UUID4,
        submenu_id: UUID4,
        dish_id: UUID4,
        update_data: UpdateDish,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        dish_service: DishService = Depends(dish_service_stub)
) -> Union[OutputDish, DishNotFoundError, DishEmptyRequestBodyError]:
    try:
        return await dish_service.update_dish(uow, str(submenu_id), str(dish_id), update_data)
    except DishDataEmpty:
        return DishEmptyRequestBodyError()
    except DishNotExists:
        return DishNotFoundError()
