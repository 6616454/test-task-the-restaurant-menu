from typing import Optional, Union

from fastapi import APIRouter, Depends, status, Response
from pydantic import UUID4

from src.api.di import uow_provider, menu_service_stub
from src.api.handlers.responses.exceptions import MenuNotFoundError, MenuAlreadyExistsError, \
    MenuEmptyRequestBodyError
from src.api.handlers.responses.menu import MenuDeleteResponse
from src.domain.menu.exceptions.menu import MenuNotExists, MenuAlreadyExists, MenuDataEmpty
from src.domain.menu.schemas.menu import OutputMenu, CreateMenu, UpdateMenu
from src.domain.menu.usecases.menu import MenuService
from src.infrastructure.db.repositories.holder import SQLAlchemyUoW

router = APIRouter(
    prefix='/api/v1/menus',
    tags=['menus']
)


# Menu Routes

@router.get(
    '/{menu_id}',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': MenuNotFoundError
        }
    }
)
async def get_menu(
        menu_id: UUID4,
        response: Response,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub)
) -> Union[OutputMenu, MenuNotFoundError]:
    try:
        return await menu_service.get_menu(uow, str(menu_id))
    except MenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return MenuNotFoundError()


@router.get('/')
async def get_menus(
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub)
) -> Optional[list[OutputMenu]]:
    return await menu_service.get_menus(uow)


@router.post(
    '/',
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': MenuAlreadyExistsError
        }
    },
    status_code=status.HTTP_201_CREATED
)
async def create_menu(
        data: CreateMenu,
        response: Response,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub)
) -> Union[OutputMenu, MenuAlreadyExistsError]:
    try:
        return await menu_service.create_menu(uow, data)
    except MenuAlreadyExists:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return MenuAlreadyExistsError()


@router.delete(
    '/{menu_id}',
    responses={
        status.HTTP_200_OK: {
            'model': MenuDeleteResponse
        },
        status.HTTP_404_NOT_FOUND: {
            'model': MenuNotFoundError
        }
    }
)
async def delete_menu(
        menu_id: UUID4,
        response: Response,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub)
):
    try:
        await menu_service.delete_menu(uow, str(menu_id))
        return MenuDeleteResponse()
    except MenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return MenuNotFoundError()


@router.patch(
    '/{menu_id}',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': MenuNotFoundError
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': MenuEmptyRequestBodyError
        }
    }
)
async def update_menu(
        menu_id: UUID4,
        update_data: UpdateMenu,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub)
) -> Union[OutputMenu, MenuNotFoundError, MenuEmptyRequestBodyError]:
    try:
        return await menu_service.update_menu(uow, str(menu_id), update_data)
    except MenuDataEmpty:
        return MenuEmptyRequestBodyError()
    except MenuNotExists:
        return MenuNotFoundError()
