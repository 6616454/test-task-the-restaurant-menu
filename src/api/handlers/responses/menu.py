from pydantic import BaseModel, Field


class MenuDeleteResponse(BaseModel):
    status: bool = True
    message: str = Field("The menu has been deleted", const=True)


class SubMenuDeleteResponse(MenuDeleteResponse):
    message: str = Field("The submenu has been deleted", const=True)


class DishDeleteResponse(MenuDeleteResponse):
    message: str = Field("The dish has been deleted", const=True)
