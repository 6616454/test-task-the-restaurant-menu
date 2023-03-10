import uuid

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import ORJSONResponse
from pydantic import UUID4

from src.domain.menu.dto.menu import CreateMenu, OutputMenu, UpdateMenu
from src.domain.menu.exceptions.menu import (
    MenuAlreadyExists,
    MenuDataEmpty,
    MenuNotExists,
)
from src.domain.menu.usecases.menu import MenuService
from src.infrastructure.db.uow import SQLAlchemyUoW
from src.presentation.api.di import get_menu_service, uow_provider
from src.presentation.api.handlers.requests.menu import (
    CreateRequestMenu,
    UpdateRequestMenu,
)
from src.presentation.api.handlers.responses.exceptions.menu import (
    MenuAlreadyExistsError,
    MenuEmptyRequestBodyError,
    MenuNotFoundError,
)
from src.presentation.api.handlers.responses.menu import MenuDeleteResponse

router = APIRouter(prefix="/api/v1/menus", tags=["menus"])


# Menu Routes


@router.get(
    "/{menu_id}",
    responses={status.HTTP_404_NOT_FOUND: {"model": MenuNotFoundError}},
    summary="Get menu",
    description="Getting the menu by ID",
)
async def get_menu(
    menu_id: UUID4,
    response: Response,
    menu_service: MenuService = Depends(get_menu_service),
) -> OutputMenu | MenuNotFoundError:
    try:
        return await menu_service.get_menu(str(menu_id))  # type: ignore
    except MenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return MenuNotFoundError()


@router.get("/", summary="Get menus", description="Getting the full menu list")
async def get_menus(
    menu_service: MenuService = Depends(get_menu_service),
) -> list[OutputMenu] | None:
    return await menu_service.get_menus()  # type: ignore


@router.post(
    "/",
    responses={status.HTTP_409_CONFLICT: {"model": MenuAlreadyExistsError}},
    status_code=status.HTTP_201_CREATED,
    summary="Create menu",
    description="Creating a new menu",
)
async def create_menu(
    data: CreateRequestMenu,
    response: Response,
    menu_service: MenuService = Depends(get_menu_service),
) -> OutputMenu | MenuAlreadyExistsError:
    try:
        return await menu_service.create_menu(CreateMenu(**data.dict()))
    except MenuAlreadyExists:
        response.status_code = status.HTTP_409_CONFLICT
        return MenuAlreadyExistsError()


@router.delete(
    "/{menu_id}",
    responses={
        status.HTTP_200_OK: {"model": MenuDeleteResponse},
        status.HTTP_404_NOT_FOUND: {"model": MenuNotFoundError},
    },
    summary="Delete menu",
    description="Deleting the menu by ID",
)
async def delete_menu(
    menu_id: UUID4,
    response: Response,
    menu_service: MenuService = Depends(get_menu_service),
):
    try:
        await menu_service.delete_menu(str(menu_id))
        return MenuDeleteResponse()
    except MenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return MenuNotFoundError()


@router.patch(
    "/{menu_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": MenuNotFoundError},
        status.HTTP_400_BAD_REQUEST: {"model": MenuEmptyRequestBodyError},
        status.HTTP_409_CONFLICT: {"model": MenuAlreadyExistsError},
    },
    summary="Update menu",
    description="Updating the menu by ID",
)
async def update_menu(
    menu_id: UUID4,
    update_data: UpdateRequestMenu,
    response: Response,
    menu_service: MenuService = Depends(get_menu_service),
) -> OutputMenu | MenuNotFoundError | MenuEmptyRequestBodyError:
    try:
        return await menu_service.update_menu(
            UpdateMenu(menu_id=str(menu_id), **update_data.dict())
        )  # type: ignore
    except MenuDataEmpty:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return MenuEmptyRequestBodyError()
    except MenuAlreadyExists:
        response.status_code = status.HTTP_409_CONFLICT
        return MenuAlreadyExistsError()
    except MenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return MenuNotFoundError()


@router.post(
    "/create_test_data",
    summary="Create test data",
    description="Creating test data for test use application",
)
async def create_test_data(uow: SQLAlchemyUoW = Depends(uow_provider)) -> None:
    """Endpoint for the examiner"""

    FirstMenu = uow.menu_holder.menu_repo._model(
        id=str(uuid.uuid4()), title="???????????? ????????", description="???????????????? ?????????????? ????????"
    )

    SecondMenu = uow.menu_holder.menu_repo._model(
        id=str(uuid.uuid4()), title="???????????? ????????", description="???????????????? ?????????????? ????????"
    )

    await uow.menu_holder.menu_repo.save(FirstMenu)
    await uow.menu_holder.menu_repo.save(SecondMenu)

    await uow.commit()

    FirstSubMenu = uow.menu_holder.submenu_repo._model(
        id=str(uuid.uuid4()),
        title="???????????? ??????????????",
        description="???????????????? ?????????????? ??????????????",
        menu_id=FirstMenu.id,
    )
    SecondSubMenu = uow.menu_holder.submenu_repo._model(
        id=str(uuid.uuid4()),
        title="???????????? ??????????????",
        description="???????????????? ?????????????? ??????????????",
        menu_id=FirstMenu.id,
    )
    ThirdSubMenu = uow.menu_holder.submenu_repo._model(
        id=str(uuid.uuid4()),
        title="???????????? ??????????????",
        description="???????????????? ???????????????? ??????????????",
        menu_id=SecondMenu.id,
    )

    await uow.menu_holder.submenu_repo.save(FirstSubMenu)
    await uow.menu_holder.submenu_repo.save(SecondSubMenu)
    await uow.menu_holder.submenu_repo.save(ThirdSubMenu)

    await uow.commit()

    FirstDish = uow.menu_holder.dish_repo._model(
        id=str(uuid.uuid4()),
        title="???????????????? ?????????????? ??????????",
        description="???????????????? ?????????????? ??????????",
        price="250.12",
        submenu_id=FirstSubMenu.id,
    )

    SecondDish = uow.menu_holder.dish_repo._model(
        id=str(uuid.uuid4()),
        title="???????????????? ?????????????? ??????????",
        description="???????????????? ?????????????? ??????????",
        price="123.12",
        submenu_id=FirstSubMenu.id,
    )
    ThirdDish = uow.menu_holder.dish_repo._model(
        id=str(uuid.uuid4()),
        title="???????????????? ???????????????? ??????????",
        description="???????????????? ???????????????? ??????????",
        price="250.12",
        submenu_id=SecondSubMenu.id,
    )
    FourthDish = uow.menu_holder.dish_repo._model(
        id=str(uuid.uuid4()),
        title="???????????????? ???????????????????? ??????????",
        description="???????????????? ???????????????????? ??????????",
        price="250.12",
        submenu_id=ThirdSubMenu.id,
    )

    await uow.menu_holder.dish_repo.save(FirstDish)
    await uow.menu_holder.dish_repo.save(SecondDish)
    await uow.menu_holder.dish_repo.save(ThirdDish)
    await uow.menu_holder.dish_repo.save(FourthDish)

    await uow.commit()

    return ORJSONResponse(content={"detail": "Test data was created"})
