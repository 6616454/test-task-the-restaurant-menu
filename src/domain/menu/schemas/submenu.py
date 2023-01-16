from pydantic import BaseModel, UUID4


class BaseSubMenu(BaseModel):
    title: str
    description: str


class OutputSubMenu(BaseModel):
    # Продублировал отдельно, чтобы подогнать под тесты

    id: UUID4
    title: str
    description: str
    dishes_count: int = 0

    class Config:
        orm_mode = True


class CreateSubMenu(BaseSubMenu):
    pass


class UpdateSubMenu(BaseSubMenu):
    title: str = None
    description: str = None
