import uuid

from fastapi import APIRouter, Depends, Response, status
from pydantic import UUID4

from src.domain.menu.dto.menu import CreateMenu, OutputMenu, UpdateMenu
from src.domain.menu.exceptions.menu import (
    MenuAlreadyExists,
    MenuDataEmpty,
    MenuNotExists,
)
from src.domain.menu.usecases.menu import MenuService
from src.infrastructure.db.uow import SQLAlchemyUoW
from src.presentation.api.di import menu_service_stub, uow_provider
from src.presentation.api.handlers.requests.menu import (
    CreateRequestMenu,
    UpdateRequestMenu,
)
from src.presentation.api.handlers.responses.exceptions import (
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
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub),
) -> OutputMenu | MenuNotFoundError:
    try:
        return await menu_service.get_menu(uow, str(menu_id))  # type: ignore
    except MenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return MenuNotFoundError()


@router.get("/", summary="Get menus", description="Getting the full menu list")
async def get_menus(
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub),
) -> list[OutputMenu] | None:
    return await menu_service.get_menus(uow)  # type: ignore


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
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub),
) -> OutputMenu | MenuAlreadyExistsError:
    try:
        return await menu_service.create_menu(uow, CreateMenu(**data.dict()))  # type: ignore
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
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub),
):
    try:
        await menu_service.delete_menu(uow, str(menu_id))  # type: ignore
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
        uow: SQLAlchemyUoW = Depends(uow_provider),
        menu_service: MenuService = Depends(menu_service_stub),
) -> OutputMenu | MenuNotFoundError | MenuEmptyRequestBodyError:
    try:
        return await menu_service.update_menu(
            uow, UpdateMenu(menu_id=str(menu_id), **update_data.dict())  # type: ignore
        )
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
    summary='Create test data',
    description='Creating test data for test use application'
)
async def create_test_data(uow: SQLAlchemyUoW = Depends(uow_provider)) -> None:
    FirstMenu = uow.menu_holder.menu_repo.model(
        id=str(uuid.uuid4()), title="Первое меню", description="Описание первого меню"
    )

    SecondMenu = uow.menu_holder.menu_repo.model(
        id=str(uuid.uuid4()), title="Второе меню", description="Описание второго меню"
    )

    await uow.menu_holder.menu_repo.save(FirstMenu)
    await uow.menu_holder.menu_repo.save(SecondMenu)

    await uow.commit()

    FirstSubMenu = uow.menu_holder.submenu_repo.model(
        id=str(uuid.uuid4()),
        title="Первое подменю",
        description="Описание первого подменю",
        menu_id=FirstMenu.id,
    )
    SecondSubMenu = uow.menu_holder.submenu_repo.model(
        id=str(uuid.uuid4()),
        title="Второе подменю",
        description="Описание второго подменю",
        menu_id=FirstMenu.id,
    )
    ThirdSubMenu = uow.menu_holder.submenu_repo.model(
        id=str(uuid.uuid4()),
        title="Третье подменю",
        description="Описание третьего подменю",
        menu_id=SecondMenu.id,
    )

    await uow.menu_holder.submenu_repo.save(FirstSubMenu)
    await uow.menu_holder.submenu_repo.save(SecondSubMenu)
    await uow.menu_holder.submenu_repo.save(ThirdSubMenu)

    await uow.commit()

    FirstDish = uow.menu_holder.dish_repo.model(
        id=str(uuid.uuid4()),
        title="Название первого блюда",
        description="Описание первого блюда",
        price="250.12",
        submenu_id=FirstSubMenu.id,
    )

    SecondDish = uow.menu_holder.dish_repo.model(
        id=str(uuid.uuid4()),
        title="Название второго блюда",
        description="Описание второго блюда",
        price="123.12",
        submenu_id=FirstSubMenu.id,
    )
    ThirdDish = uow.menu_holder.dish_repo.model(
        id=str(uuid.uuid4()),
        title="Название третьего блюда",
        description="Описание третьего блюда",
        price="250.12",
        submenu_id=SecondSubMenu.id,
    )
    FourthDish = uow.menu_holder.dish_repo.model(
        id=str(uuid.uuid4()),
        title="Название четвертого блюда",
        description="Описание четвертого блюда",
        price="250.12",
        submenu_id=ThirdSubMenu.id,
    )

    await uow.menu_holder.dish_repo.save(FirstDish)
    await uow.menu_holder.dish_repo.save(SecondDish)
    await uow.menu_holder.dish_repo.save(ThirdDish)
    await uow.menu_holder.dish_repo.save(FourthDish)

    await uow.commit()
