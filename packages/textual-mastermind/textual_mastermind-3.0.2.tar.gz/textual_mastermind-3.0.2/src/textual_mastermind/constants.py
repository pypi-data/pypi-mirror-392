from pathlib import Path
from typing import Final

CONFIG_FILE: Final[Path] = Path(__file__).parent / "config.toml"

LOCALE_DIR: Final[Path] = Path(__file__).parent / "locale"
