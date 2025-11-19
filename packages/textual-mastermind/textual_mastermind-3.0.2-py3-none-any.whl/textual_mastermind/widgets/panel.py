from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widgets import Button

from ..app_config import app_config


class ColorButton(Button):
    class Toggled(Message):
        def __init__(self, sender: "ColorButton") -> None:
            super().__init__()
            self.sender = sender

    def on_click(self):
        self.post_message(self.Toggled(sender=self))


class Panel(VerticalScroll):
    def __init__(self) -> None:
        super().__init__()
        self.active_color = 0

    def compose(self) -> ComposeResult:
        variation = app_config.variation

        self.color_buttons: list[ColorButton] = [
            ColorButton(app_config.ui["blank_color"], classes="color_button active")
        ]

        self.color_buttons.extend(
            [
                ColorButton(color, classes="color_button")
                for color in app_config.ui["code_peg_colors"][: variation["num_colors"]]
            ]
        )

        for color_button in self.color_buttons:
            yield color_button

    def on_color_button_toggled(self, message: ColorButton.Toggled):
        for color_button in self.color_buttons:
            color_button.remove_class("active")

        message.sender.add_class("active")

        self.active_color = self.color_buttons.index(message.sender)
