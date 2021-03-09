from fastapi import FastAPI

from data.requests import OrderColourRequest
from requests import OrderRequest


class Endpoints:
    subapp = FastAPI()

    def __init__(self, service, app: FastAPI):
        self.service = service
        app.mount("/order", self.subapp)

    @subapp.post("/order/accepted")
    def order_accepted(self, request: OrderRequest):
        self.service.handle_order_accept()

    @subapp.post("/order/rejected")
    def order_rejected(self, request: OrderRequest):
        self.service.handle_order_reject()

    @subapp.post("/order/ready")
    def order_ready(self, request: OrderColourRequest):
        self.service.handle_order_ready(request.colour)

    @subapp.post("/order/done")
    def order_done(self, request: OrderRequest):
        self.service.handle_order_done()
