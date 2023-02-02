from pydantic import BaseModel


class CreateRequestMenu(BaseModel):
    title: str
    description: str


class CreateRequestSubMenu(CreateRequestMenu):
    pass


class CreateRequestDish(CreateRequestMenu):
    price: str


class UpdateRequestMenu(BaseModel):
    title: str | None = None
    description: str | None = None


class UpdateRequestSubMenu(UpdateRequestMenu):
    pass


class UpdateRequestDish(UpdateRequestMenu):
    price: str | None = None
