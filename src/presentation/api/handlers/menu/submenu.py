from fastapi import APIRouter, Depends, Response, status
from pydantic import UUID4

from src.domain.menu.dto.submenu import CreateSubMenu, OutputSubMenu, UpdateSubMenu
from src.domain.menu.exceptions.menu import MenuNotExists
from src.domain.menu.exceptions.submenu import (
    SubMenuAlreadyExists,
    SubMenuDataEmpty,
    SubMenuNotExists,
)
from src.domain.menu.usecases.submenu import SubMenuService
from src.presentation.api.di import get_submenu_service
from src.presentation.api.handlers.requests.menu import (
    CreateRequestSubMenu,
    UpdateRequestSubMenu,
)
from src.presentation.api.handlers.responses.exceptions import (
    MenuNotFoundError,
    SubMenuAlreadyExistsError,
    SubMenuEmptyRequestBodyError,
    SubMenuNotFoundError,
)
from src.presentation.api.handlers.responses.menu import SubMenuDeleteResponse

router = APIRouter(prefix="/api/v1/menus", tags=["submenus"])


# Submenu Routes


@router.get(
    "/{menu_id}/submenus",
    responses={status.HTTP_404_NOT_FOUND: {"model": MenuNotFoundError}},
    summary="Get submenus",
    description="Getting a complete list of submenus of a specific menu",
)
async def get_submenus(
    menu_id: UUID4,
    response: Response,
    submenu_service: SubMenuService = Depends(get_submenu_service),
) -> list[OutputSubMenu] | MenuNotFoundError | None:
    try:
        return await submenu_service.get_submenus(str(menu_id))  # type: ignore
    except MenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return MenuNotFoundError()


@router.get(
    "/{menu_id}/submenus/{submenu_id}",
    responses={status.HTTP_404_NOT_FOUND: {"model": SubMenuNotFoundError}},
    summary="Get submenu",
    description="Getting a specific submenu by menu and ID",
)
async def get_submenu(
    menu_id: UUID4,
    submenu_id: UUID4,
    response: Response,
    menu_service: SubMenuService = Depends(get_submenu_service),
) -> OutputSubMenu | SubMenuNotFoundError:
    try:
        return await menu_service.get_submenu(str(menu_id), str(submenu_id))  # type: ignore
    except SubMenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return SubMenuNotFoundError()


@router.post(
    "/{menu_id}/submenus",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": SubMenuAlreadyExistsError},
        status.HTTP_404_NOT_FOUND: {"model": MenuNotFoundError},
    },
    status_code=status.HTTP_201_CREATED,
    summary="Create submenu",
    description="Creating a new submenu for the menu",
)
async def create_submenu(
    data: CreateRequestSubMenu,
    menu_id: UUID4,
    response: Response,
    menu_service: SubMenuService = Depends(get_submenu_service),
) -> OutputSubMenu | SubMenuAlreadyExistsError | MenuNotFoundError:
    try:
        return await menu_service.create_submenu(
            CreateSubMenu(menu_id=str(menu_id), **data.dict())
        )
    except SubMenuAlreadyExists:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return SubMenuAlreadyExistsError()
    except MenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return MenuNotFoundError()


@router.delete(
    "/{menu_id}/submenus/{submenu_id}",
    responses={
        status.HTTP_200_OK: {"model": SubMenuDeleteResponse},
        status.HTTP_404_NOT_FOUND: {"model": SubMenuNotFoundError},
    },
    summary="Delete submenu",
    description="Deleting a submenu of a certain menu by ID",
)
async def delete_submenu(
    submenu_id: UUID4,
    menu_id: UUID4,
    response: Response,
    submenu_service: SubMenuService = Depends(get_submenu_service),
):
    try:
        await submenu_service.delete_submenu(str(menu_id), str(submenu_id))
        return SubMenuDeleteResponse()
    except SubMenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return SubMenuNotFoundError()


@router.patch(
    "/{menu_id}/submenus/{submenu_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": SubMenuNotFoundError},
        status.HTTP_400_BAD_REQUEST: {"model": SubMenuEmptyRequestBodyError},
        status.HTTP_409_CONFLICT: {"model": SubMenuAlreadyExistsError},
    },
    summary="Update submenu",
    description="Updating a submenu of a certain menu by ID",
)
async def update_submenu(
    menu_id: UUID4,
    submenu_id: UUID4,
    update_data: UpdateRequestSubMenu,
    response: Response,
    submenu_service: SubMenuService = Depends(get_submenu_service),
) -> OutputSubMenu | SubMenuNotFoundError | SubMenuEmptyRequestBodyError:
    try:
        return await submenu_service.update_submenu(
            UpdateSubMenu(
                menu_id=str(menu_id), submenu_id=str(submenu_id), **update_data.dict()
            )  # type: ignore
        )
    except SubMenuDataEmpty:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return SubMenuEmptyRequestBodyError()
    except SubMenuAlreadyExists:
        response.status_code = status.HTTP_409_CONFLICT
        return SubMenuAlreadyExistsError()
    except SubMenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return SubMenuNotFoundError()
