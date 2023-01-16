from pydantic import BaseModel, Field


class DishDeleteResponse(BaseModel):
    status: bool = True
    message: str = Field("The dish has been deleted", const=True)
