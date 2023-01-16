from pydantic import BaseModel, validator, UUID4


class BaseDish(BaseModel):
    title: str
    description: str
    price: str

    @validator('price')
    def price_validator(cls, v):
        return '{:.2f}'.format(round(float(v), 2))


class OutputDish(BaseModel):
    # Продублировал отдельно, чтобы подогнать под тесты
    id: UUID4
    title: str
    description: str
    price: str

    class Config:
        orm_mode = True


class CreateDish(BaseDish):
    pass


class UpdateDish(BaseDish):
    title: str = None
    description: str = None
    price: float = None
