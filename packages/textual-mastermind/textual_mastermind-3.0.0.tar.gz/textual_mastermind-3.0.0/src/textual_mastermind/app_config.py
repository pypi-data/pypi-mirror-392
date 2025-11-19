from dataclasses import dataclass
from typing import TypedDict

from tilsit_config.settings import SettingBoolean, SettingOptions


class Ui(TypedDict):
    icon: str
    blank_color: str
    code_peg_colors: list[str]
    feedback_peg_colors: list[str]
    check_default_text: str
    check_hover_text: str


@dataclass
class Settings:
    language: SettingOptions
    variation: SettingOptions
    blank_color: SettingBoolean
    duplicate_colors: SettingBoolean


class Variation(TypedDict):
    num_rows: int
    num_pegs: int
    num_colors: int


class AppConfig:
    ui: Ui
    settings: Settings
    variations: dict[str, Variation]

    def init(self, ui: Ui, settings: Settings, variations: dict[str, Variation]):
        self.ui = ui
        self.settings = settings
        self.variations = variations

    @property
    def variation(self) -> Variation:
        return self.variations[self.settings.variation.current_value]


app_config = AppConfig()
