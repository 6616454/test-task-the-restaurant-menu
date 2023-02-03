from pydantic import BaseModel, validator


class CreateRequestMenu(BaseModel):
    title: str
    description: str


class CreateRequestSubMenu(CreateRequestMenu):
    pass


class CreateRequestDish(CreateRequestMenu):
    price: str

    @validator("price")
    def price_validator(cls, v):
        try:
            return f"{round(float(v), 2):.2f}"
        except ValueError:
            pass


class UpdateRequestMenu(BaseModel):
    title: str | None = None
    description: str | None = None


class UpdateRequestSubMenu(UpdateRequestMenu):
    pass


class UpdateRequestDish(UpdateRequestMenu):
    price: str | None = None

    @validator("price")
    def price_validator(cls, v):
        try:
            if v is None:
                return
            return f"{round(float(v), 2):.2f}"
        except ValueError:
            return {"detail": "Invalid data"}
