from typing import Final

from textual.binding import Binding

GlOBAL_BINDINGS: Final[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
    Binding(
        key="ctrl+q",
        action="quit",
        description="Quit",
        key_display="Ctrl+Q",
        show=True,
    ),
    Binding(
        key="ctrl+c",
        action="nothing",
        description="",
    ),
    Binding(
        key="f2",
        action="new_game",
        description="New game",
        key_display="F2",
    ),
    Binding(
        key="f3",
        action="settings",
        description="Settings",
        key_display="F3",
    ),
]
