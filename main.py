from multiprocessing.context import Process

import uvicorn
from fastapi import FastAPI

from interface import DummyInterface

app = FastAPI()
interface = DummyInterface(app)

if __name__ == '__main__':
    proc = Process(target=uvicorn.run,
                        args=(app,),
                        daemon=True)
    proc.start()
    while True:
        action = input("Please provide value, 1-8 for buttons, + for add, - for remove, P for pay: \n")
        if action == "+":
            interface.button_plus_press()
        elif action == "-":
            interface.button_minus_press()
        elif action == "P":
            interface.button_pay_press()
        else:
            interface.button_beverage_press(int(action) - 1)
        interface.print_state()