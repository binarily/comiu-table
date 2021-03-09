from pydantic import BaseModel


class Colour(BaseModel):
    colour: int
    segment: int


class OrderId(BaseModel):
    id: int


class OrderColourRequest(BaseModel):
    orderId: OrderId
    status: str
    colour: Colour