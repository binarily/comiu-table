from pydantic import BaseModel

from data.requests import OrderId


class OrderRequest(BaseModel):
    order_id: OrderId
    status: str