from dataclasses import fields, replace
from importlib.metadata import metadata
from typing import Any, cast

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.events import Click
from textual.widgets import Button, Footer, Header, Label
from textual_utils import (
    AboutHeaderIcon,
    AppMetadata,
    ConfirmScreen,
    SettingsScreen,
    mount_about_header_icon,
)
from tilsit_config import load_config, save_settings
from tilsit_i18n import tr

from .app_config import Settings, app_config
from .bindings import GlOBAL_BINDINGS
from .constants import (
    CONFIG_FILE,
    LOCALE_DIR,
)
from .game import Game
from .widgets.board import Board
from .widgets.panel import Panel


class MastermindApp(App[None]):
    CSS_PATH = "styles.tcss"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = GlOBAL_BINDINGS

    def __init__(self) -> None:
        super().__init__()

        config_dict, settings = cast(
            tuple[dict[str, Any], Settings],
            load_config(config_file=str(CONFIG_FILE), settings_cls=Settings),
        )

        app_config.init(
            ui=config_dict["ui"],
            settings=settings,
            variations=config_dict["variations"],
        )

        pkg_name = cast(str, __package__)
        pkg_metadata = metadata(pkg_name)

        self.app_metadata = AppMetadata(
            name="Mastermind",
            version=pkg_metadata["Version"],
            icon=app_config.ui["icon"],
            description="Break the hidden code",
            author=pkg_metadata["Author"],
            email=pkg_metadata["Author-email"].split("<")[1][:-1],
        )

        tr.localedir = LOCALE_DIR
        tr.language = app_config.settings.language.current_value

        self.translate_bindings()

        self.panel: Panel
        self.board: Board
        self.game: Game

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(id="body")
        yield Footer()

    async def on_mount(self) -> None:
        await mount_about_header_icon(
            current_app=self,
            app_metadata=self.app_metadata,
        )
        self.translate_about_header_icon()

        self.title = self.app_metadata.name

        self.create_new_game()

    def translate_bindings(self) -> None:
        for binding in GlOBAL_BINDINGS:
            if isinstance(binding, Binding):
                key = binding.key
                current_binding: Binding = self._bindings.key_to_bindings[key][0]
                self._bindings.key_to_bindings[key] = [
                    replace(current_binding, description=tr(binding.description))
                ]

    def translate_about_header_icon(self) -> None:
        about_header_icon: AboutHeaderIcon = self.query_one(AboutHeaderIcon)
        about_header_icon.tooltip = tr("About")

    def translate(self) -> None:
        self.translate_bindings()
        self.translate_about_header_icon()

    def create_new_game(self) -> None:
        if hasattr(self, "game"):
            self.panel.remove()
            self.board.remove()

        self.panel = Panel()
        self.board = Board()
        body: Horizontal = self.query_one("#body", Horizontal)
        body.mount(self.panel)
        body.mount(self.board)

        self.game = Game()

    @on(Button.Pressed, ".code_peg")
    def on_code_peg_pressed(self, event: Button.Pressed):
        active_color: int = self.panel.active_color
        if active_color != 0:
            event.button.label = app_config.ui["code_peg_colors"][active_color - 1]
        else:
            event.button.label = app_config.ui["blank_color"]

    @on(Click, ".check")
    def on_check_click(self) -> None:
        breaker_code: list[int] = []
        for code_peg in self.board.current_row.code_pegs:
            color_str = cast(str, code_peg.label)

            color: int
            if color_str == app_config.ui["blank_color"]:
                color = 0
            else:
                color = app_config.ui["code_peg_colors"].index(color_str) + 1

            breaker_code.append(color)

        num_red_pegs: int
        num_white_pegs: int
        num_red_pegs, num_white_pegs = self.game.check_code(breaker_code)

        self.board.current_row.query_one("#check").remove()

        self.board.current_row.mount(
            Label(
                "".join(
                    [
                        (app_config.ui["feedback_peg_colors"][0] + " ") * num_red_pegs,
                        (app_config.ui["feedback_peg_colors"][1] + " ")
                        * num_white_pegs,
                        (app_config.ui["blank_color"] + " ")
                        * (self.game.num_pegs - num_red_pegs - num_white_pegs),
                    ]
                ),
                classes="feedback_pegs",
            )
        )

        self.board.current_row.disabled = True

        if num_red_pegs == self.game.num_pegs:
            self.notify(tr("Congratulations!"))
        else:
            if self.board.current_row_number < self.game.num_rows:
                self.board.add_row()
            else:
                maker_code: list[int] = self.game.get_maker_code()
                maker_code_str: str = ""
                for color in maker_code:
                    if color == 0:
                        maker_code_str += app_config.ui["blank_color"] + " "
                    else:
                        maker_code_str += (
                            app_config.ui["code_peg_colors"][color - 1] + " "
                        )

                self.notify(
                    f"{tr('Better luck next time')}\n{tr('Code')}: {maker_code_str}",
                    timeout=30,
                )

    @work
    async def action_new_game(self) -> None:
        if await self.push_screen_wait(
            ConfirmScreen(
                dialog_title="New game",
                dialog_subtitle=self.app_metadata.name,
                question="Are you sure you want to start a new game?",
            )
        ):
            self.create_new_game()

    @work
    async def action_settings(self) -> None:
        if await self.push_screen_wait(
            SettingsScreen(
                dialog_title="Settings",
                dialog_subtitle=self.app_metadata.name,
                settings=[
                    getattr(app_config.settings, field.name)
                    for field in fields(app_config.settings)
                ],
            )
        ):
            settings_changed = False

            if app_config.settings.language.changed:
                settings_changed = True

                tr.language = app_config.settings.language.current_value
                self.translate()

            if any(
                [
                    app_config.settings.variation.changed,
                    app_config.settings.duplicate_colors.changed,
                    app_config.settings.blank_color.changed,
                ]
            ):
                settings_changed = True

                self.notify(
                    tr("New game settings will be applied to a new game"), timeout=3
                )

            if settings_changed:
                save_settings(str(CONFIG_FILE), app_config.settings)
