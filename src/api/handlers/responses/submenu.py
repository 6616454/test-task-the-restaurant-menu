from pydantic import BaseModel, Field


class SubMenuDeleteResponse(BaseModel):
    status: bool = True
    message: str = Field("The submenu has been deleted", const=True)