from pydantic import BaseModel


class DTO(BaseModel):
    class Config:
        orm_mode = True
