from fastapi import APIRouter, Depends, Response, status
from pydantic import UUID4, ValidationError

from src.domain.menu.dto.dish import CreateDish, OutputDish, UpdateDish
from src.domain.menu.exceptions.dish import (
    DishAlreadyExists,
    DishDataEmpty,
    DishNotExists,
)
from src.domain.menu.exceptions.submenu import SubMenuNotExists
from src.domain.menu.usecases.dish import DishService
from src.infrastructure.db.uow import SQLAlchemyUoW
from src.presentation.api.di import dish_service_stub, uow_provider
from src.presentation.api.handlers.requests.menu import (
    CreateRequestDish,
    UpdateRequestDish,
)
from src.presentation.api.handlers.responses.exceptions import (
    DishAlreadyExistsError,
    DishEmptyRequestBodyError,
    DishNotFoundError,
    DishPriceValidationError,
    SubMenuNotFoundError,
)
from src.presentation.api.handlers.responses.menu import DishDeleteResponse

router = APIRouter(prefix="/api/v1/menus", tags=["dishes"])


# Dish Routes


@router.get(
    "/{menu_id}/submenus/{submenu_id}/dishes",
    responses={status.HTTP_404_NOT_FOUND: {"model": SubMenuNotFoundError}},
)
async def get_dishes(
    menu_id: UUID4,
    submenu_id: UUID4,
    uow: SQLAlchemyUoW = Depends(uow_provider),
    dish_service: DishService = Depends(dish_service_stub),
) -> list[OutputDish]:  # , SubMenuNotFoundError]
    # try:
    return await dish_service.get_dishes(uow, str(menu_id), str(submenu_id))  # type: ignore
    # except SubMenuNotExists:
    #     response.status_code = status.HTTP_404_NOT_FOUND
    #     return SubMenuNotFoundError()


@router.get(
    "/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    responses={status.HTTP_404_NOT_FOUND: {"model": DishNotFoundError}},
)
async def get_dish(
    menu_id: UUID4,
    submenu_id: UUID4,
    dish_id: UUID4,
    response: Response,
    uow: SQLAlchemyUoW = Depends(uow_provider),
    dish_service: DishService = Depends(dish_service_stub),
) -> OutputDish | DishNotFoundError:
    try:
        return await dish_service.get_dish(uow, str(submenu_id), str(dish_id))  # type: ignore
    except DishNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DishNotFoundError()


@router.post(
    "/{menu_id}/submenus/{submenu_id}/dishes",
    responses={
        status.HTTP_409_CONFLICT: {"model": DishAlreadyExistsError},
        status.HTTP_404_NOT_FOUND: {"model": SubMenuNotFoundError},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": DishPriceValidationError},
    },
    status_code=status.HTTP_201_CREATED,
)
async def create_dish(
    menu_id: UUID4,
    submenu_id: UUID4,
    response: Response,
    data: CreateRequestDish,
    uow: SQLAlchemyUoW = Depends(uow_provider),
    dish_service: DishService = Depends(dish_service_stub),
) -> OutputDish | SubMenuNotFoundError | DishAlreadyExistsError | DishPriceValidationError:
    try:
        return await dish_service.create_dish(
            uow,  # type: ignore
            CreateDish(menu_id=str(menu_id), submenu_id=str(submenu_id), **data.dict()),
        )
    except SubMenuNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return SubMenuNotFoundError()
    except DishAlreadyExists:
        response.status_code = status.HTTP_409_CONFLICT
        return DishAlreadyExistsError()
    except ValidationError:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return DishPriceValidationError()


@router.delete(
    "/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    responses={
        status.HTTP_200_OK: {"model": DishDeleteResponse},
        status.HTTP_404_NOT_FOUND: {"model": DishNotFoundError},
    },
)
async def delete_dish(
    menu_id: UUID4,
    submenu_id: UUID4,
    dish_id: UUID4,
    response: Response,
    uow: SQLAlchemyUoW = Depends(uow_provider),
    dish_service: DishService = Depends(dish_service_stub),
):
    try:
        # type: ignore
        await dish_service.delete_dish(uow, str(menu_id), str(submenu_id), str(dish_id))  # type: ignore
        return DishDeleteResponse()
    except DishNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DishNotFoundError()


@router.patch(
    "/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": DishNotFoundError},
        status.HTTP_400_BAD_REQUEST: {"model": DishEmptyRequestBodyError},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": DishPriceValidationError},
        status.HTTP_409_CONFLICT: {"model": DishAlreadyExistsError},
    },
)
async def update_dish(
    menu_id: UUID4,
    submenu_id: UUID4,
    dish_id: UUID4,
    update_data: UpdateRequestDish,
    response: Response,
    uow: SQLAlchemyUoW = Depends(uow_provider),
    dish_service: DishService = Depends(dish_service_stub),
) -> OutputDish | DishNotFoundError | DishEmptyRequestBodyError | DishPriceValidationError:
    try:
        return await dish_service.update_dish(
            uow,  # type: ignore
            UpdateDish(
                menu_id=str(menu_id),
                submenu_id=str(submenu_id),
                dish_id=str(dish_id),
                **update_data.dict()
            ),
        )
    except DishDataEmpty:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return DishEmptyRequestBodyError()
    except DishNotExists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return DishNotFoundError()
    except DishAlreadyExists:
        response.status_code = status.HTTP_409_CONFLICT
        return DishAlreadyExistsError()
    except ValidationError:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return DishPriceValidationError()
