from pydantic import BaseModel


class Message(BaseModel):
    success: bool = True
    message: str


class Page(BaseModel):
    total: int
    page: int
    page_size: int
