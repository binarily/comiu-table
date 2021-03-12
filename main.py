from multiprocessing.context import Process

import uvicorn
from fastapi import FastAPI

from data.requests import *
from interface import DummyInterface

app = FastAPI()
interface = DummyInterface()


@app.post("/order/accepted")
def order_accepted(request: OrderRequest):
    interface.service.handle_order_accept()
    return {
        "orderId": request.orderId,
        "status": "OK"
    }


@app.post("/order/rejected")
def order_rejected(request: OrderRequest):
    interface.service.handle_order_reject()
    return {
        "orderId": request.orderId,
        "status": "OK"
    }


@app.post("/order/ready")
def order_ready(request: OrderColourRequest):
    interface.service.handle_order_ready(request.colour)
    return {
        "orderId": request.orderId,
        "status": "OK"
    }


@app.post("/order/done")
def order_done(request: OrderRequest):
    interface.service.handle_order_done()
    return {
        "orderId": request.orderId,
        "status": "OK"
    }


# Interface actions
@app.get("/interface/list")
def print_state():
    return interface.print_state()


@app.get("/interface/plus")
def handle_plus():
    interface.button_plus_press()
    return interface.print_state()


@app.get("/interface/minus")
def handle_minus():
    interface.button_minus_press()
    return interface.print_state()


@app.get("/interface/pay")
def handle_pay():
    interface.button_pay_press()
    return interface.print_state()


@app.get("/interface/beverage/{button}")
def handle_plus(button: int):
    interface.button_beverage_press(button)
    return interface.print_state()
