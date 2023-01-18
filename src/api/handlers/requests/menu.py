from pydantic import BaseModel


class CreateRequestMenu(BaseModel):
    title: str
    description: str


class CreateRequestSubMenu(CreateRequestMenu):
    pass


class CreateRequestDish(CreateRequestMenu):
    price: str
