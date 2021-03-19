from typing import Dict, List, Optional

from pydantic.dataclasses import dataclass

from data.LightState import LightState
from data.requests import Colour
from interface import DummyInterface
from swagger_client import OrderControllerApi, OrderRequest, Elements, OrderStatusResponse


@dataclass
class ButtonInfo:
    name: str
    price: float
    sku: int
    available: bool  # Future-proofing for eventual checks


class TableService:
    last_button: Optional[ButtonInfo] = None
    multiple_selection: bool = False
    total_amount: float = 0.0
    buttons: List[ButtonInfo] = list()
    current_order: Dict[int, int] = dict()  # sku -> quantity
    can_order: bool = True
    interface: DummyInterface
    server_api: OrderControllerApi
    device_id: int = 3
    segment_ids = {7: 0, 8: 1, 9: 2, 10: 3}

    def __init__(self, interface: DummyInterface):
        self.interface = interface
        self.server_api = OrderControllerApi()

        # Testing set-up
        self.buttons.append(ButtonInfo("Carlsberg", 12.0, 11, True))
        self.buttons.append(ButtonInfo("Tuborg", 12.0, 12, True))
        self.buttons.append(ButtonInfo("Okocim", 15.0, 13, True))
        self.buttons.append(ButtonInfo("Desperados", 15.0, 14, True))
        self.buttons.append(ButtonInfo("Sommersby", 10.0, 15, True))
        self.buttons.append(ButtonInfo("Kronenburg", 15.0, 16, True))
        self.buttons.append(ButtonInfo("Kustosz", 20.0, 17, True))
        self.buttons.append(ButtonInfo("Grolsch", 12.0, 18, True))

    def handle_beverage_button(self, number: int):
        if not self.can_order:
            return
        current_button = self.buttons[number]
        # If at least one of the orders is in multiples
        if self.multiple_selection:
            if current_button.sku not in self.current_order.keys():
                order_size = 0
            else:
                order_size = self.current_order[current_button.sku]
            # Show the screen for selecting multiples for self.last_button
            self.interface.switch_light_mode(self.buttons.index(self.last_button),
                                             LightState.ON if self.last_button.sku in self.current_order.keys()
                                             else LightState.OFF)
            self.interface.switch_light_mode(self.buttons.index(current_button), LightState.BLINKING)
            self.interface.print_on_display(
                f"Ordering {current_button.name}, \n"
                f"cost: {current_button.price}, \n"
                f"ordered: {order_size}")
        else:
            if current_button.sku in self.current_order:
                self.current_order.pop(current_button.sku)
                self.total_amount -= current_button.price
                # Empty the screen (or return to total amount)
                self.interface.switch_light_mode(self.buttons.index(current_button), LightState.OFF)
                self.interface.print_on_display(f"Total amount: {self.total_amount}")
            else:
                self.current_order[current_button.sku] = 1
                self.total_amount += current_button.price
                self.interface.switch_light_mode(self.buttons.index(current_button), LightState.ON)
                self.interface.print_on_display(
                    f"Ordering {current_button.name}, \n"
                    f"cost: {current_button.price}, \n"
                    f"ordered: {self.current_order[current_button.sku]}, "
                    f"total amount: {self.total_amount}")
        self.last_button = current_button

    def handle_add_button(self):
        if not self.can_order:
            return
        # Add button on empty history does nothing
        if self.last_button is None:
            return
        # Add button on deselected button does nothing
        if self.last_button.sku not in self.current_order.keys():
            self.current_order[self.last_button.sku] = 0
        self.multiple_selection = True
        self.current_order[self.last_button.sku] += 1
        self.total_amount += self.last_button.price
        self.interface.switch_light_mode(self.buttons.index(self.last_button), LightState.BLINKING)
        # Show the screen for selecting multiples for self.last_button
        if self.last_button.sku not in self.current_order.keys():
            order_size = 0
        else:
            order_size = self.current_order[self.last_button.sku]
        self.interface.print_on_display(
            f"Ordering {self.last_button.name}, \n"
            f"cost: {self.last_button.price}, \n"
            f"ordered: {order_size}, "
            f"total amount: {self.total_amount}")

    def handle_minus_button(self):
        if not self.can_order:
            return
        # Remove button on empty history does nothing
        if self.last_button is None:
            return
        # Remove button on deselected button does nothing
        if self.last_button.sku not in self.current_order.keys():
            return
        if self.current_order[self.last_button.sku] == 1:
            self.current_order.pop(self.last_button.sku)
            self.interface.switch_light_mode(self.buttons.index(self.last_button), LightState.OFF)
        else:
            self.current_order[self.last_button.sku] -= 1
            if max(self.current_order.values()) == 1:
                self.multiple_selection = False
                self.interface.switch_light_mode(self.buttons.index(self.last_button), LightState.ON)
        self.total_amount -= self.last_button.price
        # Show the screen for selecting multiples for self.last_button
        if self.last_button.sku not in self.current_order.keys():
            order_size = 0
        else:
            order_size = self.current_order[self.last_button.sku]
        self.interface.print_on_display(
            f"Ordering {self.last_button.name}, \n"
            f"cost: {self.last_button.price}, \n"
            f"ordered: {order_size}, "
            f"total amount: {self.total_amount}")

    def handle_pay_button(self):
        if not self.can_order:
            return
        # Turn order into request
        order_request = OrderRequest(elements=list())
        for sku, quantity in self.current_order.items():
            order_request.elements.append(Elements(quantity, sku))
        # Send request with proper data to server
        response: OrderStatusResponse = self.server_api.order_using_post(self.device_id, order_request)
        if response.status == "OK":
            self.interface.print_on_display("Waiting for payment...")
            for button in range(len(self.buttons)):
                self.interface.switch_light_mode(button, LightState.OFF)
            self.can_order = False
            self.current_order = dict()
            self.total_amount = 0.0
            self.last_button = None
            self.multiple_selection = False
        else:
            self.interface.print_on_display("Internal error, try again.")

    def handle_order_accept(self):
        self.interface.print_on_display("Payment accepted, order is being prepared.")

    def handle_order_reject(self):
        self.interface.print_on_display("Payment rejected, please try again.")
        self.can_order = True

    def handle_order_ready(self, colour: Colour):
        # Print info that order is ready
        self.interface.print_on_display(f"The order is ready, please head to counter #{self.segment_ids[colour.segment]} "
                                        f"marked by this colour.")
        # Show colours
        self.interface.set_colour(colour.colour, colour.segment)
        pass

    def handle_order_done(self):
        # Remove colour
        self.interface.remove_colour()
        # Empty the screen
        self.interface.print_on_display("Hello!")
        self.can_order = True
