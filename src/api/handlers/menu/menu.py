from fastapi import APIRouter, Depends, Response, status
from pydantic import UUID4

from src.api.di import menu_service_stub, uow_provider
from src.api.handlers.requests.menu import CreateRequestMenu, UpdateRequestMenu
from src.api.handlers.responses.exceptions import (
    MenuAlreadyExistsError,
    MenuEmptyRequestBodyError,
    MenuNotFoundError,
)
from src.api.handlers.responses.menu import MenuDeleteResponse
from src.domain.menu.dto.menu import CreateMenu, OutputMenu, UpdateMenu
from src.domain.menu.exceptions.menu import (
    MenuAlreadyExists,
    MenuDataEmpty,
    MenuNotExists,
)
from src.domain.menu.usecases.menu import MenuService
from src.infrastructure.db.uow import SQLAlchemyUoW

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
    },
    summary='Get menu',
    description='Getting the menu by ID'
)
async def get_menu(
        menu_id: UUID4,
        response: Response,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub)
) -> OutputMenu | MenuNotFoundError:
    try:
        return await menu_service.get_menu(uow, str(menu_id))
    except MenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return MenuNotFoundError()


@router.get(
    '/',
    summary='Get menus',
    description='Getting the full menu list'
)
async def get_menus(
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub)
) -> list[OutputMenu] | None:
    return await menu_service.get_menus(uow)


@router.post(
    '/',
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': MenuAlreadyExistsError
        }
    },
    status_code=status.HTTP_201_CREATED,
    summary='Create menu',
    description='Creating a new menu'
)
async def create_menu(
        data: CreateRequestMenu,
        response: Response,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub)
) -> OutputMenu | MenuAlreadyExistsError:
    try:
        return await menu_service.create_menu(uow, CreateMenu(**data.dict()))
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
    },
    summary='Delete menu',
    description='Deleting the menu by ID'
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
    },
    summary='Update menu',
    description='Updating the menu by ID'
)
async def update_menu(
        menu_id: UUID4,
        update_data: UpdateRequestMenu,
        response: Response,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub)
) -> OutputMenu | MenuNotFoundError | MenuEmptyRequestBodyError:
    try:
        return await menu_service.update_menu(uow, UpdateMenu(
            menu_id=str(menu_id),
            **update_data.dict()
        ))
    except MenuDataEmpty:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return MenuEmptyRequestBodyError()
    except MenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return MenuNotFoundError()
