from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    char_code: str
    name: str
    nominal: int
    value: float
    date: str

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    char_code: Optional[str] = None
    name: Optional[str] = None
    nominal: Optional[int] = None
    value: Optional[float] = None
    date: Optional[str] = None

class ItemResponse(ItemBase):
    id: int

    class Config:
        from_attributes = True