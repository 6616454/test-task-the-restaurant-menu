from pydantic import BaseModel, BaseSettings


class CreateRequestMenu(BaseModel):
    title: str
    description: str


class CreateRequestSubMenu(CreateRequestMenu):
    pass


class CreateRequestDish(CreateRequestMenu):
    price: str


class UpdateRequestMenu(CreateRequestMenu):
    title: str | None = None
    description: str | None = None


class UpdateRequestSubMenu(UpdateRequestMenu):
    pass


class UpdateRequestDish(UpdateRequestMenu):
    price: str | None = None
