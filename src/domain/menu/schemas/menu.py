from pydantic import BaseModel, UUID4


class BaseMenu(BaseModel):
    title: str
    description: str


class OutputMenu(BaseModel):
    # Продублировал отдельно, чтобы подогнать под тесты

    id: UUID4
    title: str
    description: str
    submenus_count: int = 0
    dishes_count: int = 0

    class Config:
        orm_mode = True


class CreateMenu(BaseMenu):
    pass


class UpdateMenu(BaseMenu):
    title: str = None
    description: str = None
