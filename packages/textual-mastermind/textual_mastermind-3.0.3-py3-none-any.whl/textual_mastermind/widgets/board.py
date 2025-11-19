from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Label

from ..app_config import app_config


class Check(Label):
    def __init__(self) -> None:
        variation = app_config.variation

        self.default_text = (
            f"{app_config.ui['check_default_text']} " * variation["num_pegs"]
        )[:-1]
        self.hover_text = (
            f"{app_config.ui['check_hover_text']} " * variation["num_pegs"]
        )[:-1]

        super().__init__(self.default_text, id="check", classes="check")

    def on_enter(self) -> None:
        self.update(self.hover_text)

    def on_leave(self) -> None:
        self.update(self.default_text)


class Row(Horizontal):
    def __init__(self, row_number: int) -> None:
        super().__init__(classes="row")

        self.row_number = row_number

        variation = app_config.variation

        self.code_pegs: list[Button] = [
            Button(label=app_config.ui["blank_color"], classes="code_peg")
            for _ in range(variation["num_pegs"])
        ]

        self.check: Check = Check()

    def compose(self) -> ComposeResult:
        yield Label(f"{self.row_number:02}", classes="num")
        for code_peg in self.code_pegs:
            yield code_peg
        yield self.check


class Board(VerticalScroll):
    def __init__(self) -> None:
        super().__init__()

        self.current_row_number = 1
        self.current_row = Row(row_number=self.current_row_number)

    def compose(self) -> ComposeResult:
        yield self.current_row

    def add_row(self):
        self.current_row_number += 1
        self.current_row = Row(row_number=self.current_row_number)
        self.mount(self.current_row)
        self.scroll_end()
