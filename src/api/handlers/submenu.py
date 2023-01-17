from typing import Union

from fastapi import status, Response, Depends, APIRouter
from pydantic import UUID4

from src.api.di import uow_provider
from src.api.di.providers.services import submenu_service_stub
from src.api.handlers.responses.exceptions import SubMenuNotFoundError, SubMenuAlreadyExistsError, \
    SubMenuEmptyRequestBodyError, MenuNotFoundError
from src.api.handlers.responses.submenu import SubMenuDeleteResponse
from src.domain.menu.exceptions.menu import MenuNotExists
from src.domain.menu.exceptions.submenu import SubMenuNotExists, SubMenuAlreadyExists, SubMenuDataEmpty
from src.domain.menu.schemas.submenu import OutputSubMenu, CreateSubMenu, UpdateSubMenu
from src.domain.menu.usecases.submenu import SubMenuService
from src.infrastructure.db.holder import SQLAlchemyUoW

router = APIRouter(
    prefix='/api/v1/menus',
    tags=['submenus']
)


# Submenu Routes

@router.get(
    '/{menu_id}/submenus',
    description='Get submenus',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': MenuNotFoundError
        }
    }
)
async def get_submenus(
        menu_id: UUID4,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        submenu_service: SubMenuService = Depends(submenu_service_stub)
) -> Union[list[OutputSubMenu], MenuNotFoundError]:
    try:
        return await submenu_service.get_submenus(uow, str(menu_id))
    except MenuNotExists:
        return MenuNotFoundError()


@router.get(
    '/{menu_id}/submenus/{submenu_id}',
    description='Get submenu by menu_id and submenu_id',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': SubMenuNotFoundError
        }
    }
)
async def get_submenu(
        menu_id: UUID4,
        submenu_id: UUID4,
        response: Response,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: SubMenuService = Depends(submenu_service_stub)
) -> Union[OutputSubMenu, SubMenuNotFoundError]:
    try:
        return await menu_service.get_submenu(uow, str(menu_id), str(submenu_id))
    except SubMenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return SubMenuNotFoundError()


@router.post(
    '/{menu_id}/submenus',
    description='Create submenu by menu_id',
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': SubMenuAlreadyExistsError
        },
        status.HTTP_404_NOT_FOUND: {
            'model': MenuNotFoundError
        }
    },
    status_code=status.HTTP_201_CREATED
)
async def create_submenu(
        data: CreateSubMenu,
        menu_id: UUID4,
        response: Response,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: SubMenuService = Depends(submenu_service_stub)
) -> Union[OutputSubMenu, SubMenuAlreadyExistsError, MenuNotFoundError]:
    try:
        return await menu_service.create_submenu(uow, str(menu_id), data)
    except SubMenuAlreadyExists:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return SubMenuAlreadyExistsError()
    except MenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return MenuNotFoundError()


@router.delete(
    '/{menu_id}/submenus/{submenu_id}',
    responses={
        status.HTTP_200_OK: {
            'model': SubMenuDeleteResponse
        },
        status.HTTP_404_NOT_FOUND: {
            'model': SubMenuNotFoundError
        },
    }
)
async def delete_submenu(
        submenu_id: UUID4,
        menu_id: UUID4,
        response: Response,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        submenu_service: SubMenuService = Depends(submenu_service_stub)
):
    try:
        await submenu_service.delete_submenu(uow, str(menu_id), str(submenu_id))
        return SubMenuDeleteResponse()
    except SubMenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return SubMenuNotFoundError()


@router.patch(
    '/{menu_id}/submenus/{submenu_id}',
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': SubMenuNotFoundError
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': SubMenuEmptyRequestBodyError
        }
    }
)
async def update_submenu(
        menu_id: UUID4,
        submenu_id: UUID4,
        update_data: UpdateSubMenu,
        uow: SQLAlchemyUoW = Depends(uow_provider),
        submenu_service: SubMenuService = Depends(submenu_service_stub)
) -> Union[OutputSubMenu, SubMenuNotFoundError, SubMenuEmptyRequestBodyError]:
    try:
        return await submenu_service.update_submenu(uow, str(menu_id), str(submenu_id), update_data)
    except SubMenuDataEmpty:
        return SubMenuEmptyRequestBodyError()
    except SubMenuNotExists:
        return SubMenuNotFoundError()
