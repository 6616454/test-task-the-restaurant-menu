from pydantic import BaseModel, Field


class MenuDeleteResponse(BaseModel):
    status: bool = True
    message: str = Field("The menu has been deleted", const=True)
