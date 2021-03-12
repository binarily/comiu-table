from typing import Optional

from data.LightState import LightState


class DummyInterface:
    button_lights = {element: LightState.OFF for element in range(8)}
    screen_text = "Hello!"
    colour: Optional[int] = None

    def __init__(self):
        import service
        self.service = service.TableService(self)

    def button_beverage_press(self, number: int):
        self.service.handle_beverage_button(number)

    def button_plus_press(self):
        self.service.handle_add_button()

    def button_minus_press(self):
        self.service.handle_minus_button()

    def button_pay_press(self):
        self.service.handle_pay_button()

    # Action buttons

    def print_on_display(self, text: str):
        self.screen_text = text

    def switch_light_mode(self, number: int, mode: LightState):
        self.button_lights[number] = mode

    def set_colour(self, number: int):
        self.colour = number

    def remove_colour(self):
        self.colour = Optional[int](None)

    def print_state(self):
        return {
            "screen_text": self.screen_text,
            "colour": self.colour,
            "buttons": self.button_lights
        }
        #result = ""
        #for index, val in enumerate(self.button_lights):
        #    result += f"Button {index} set to {val}\n"
        #result += f"Screen says: {self.screen_text}\n"
        #result += f"Colour shown: {self.colour}\n"
        #return result
