"""
Alyios Windows Functions - Windows-specific utilities for Python
"""

from .console import select_option, select_from_list, confirm, get_text_input, display_menu
from .inputs import (
    # Input capture
    get_click, get_key, get_mouse_position, on_click_event, on_key_event,
    # Input simulation
    click, move_mouse, press_key, hold_key, release_key, type_text, send_keys
)
from .dialogs import select_file, select_folder, save_file_dialog

__version__ = "0.1.0"

__all__ = [
    # Console functions
    "select_option",
    "select_from_list",
    "confirm",
    "get_text_input",
    "display_menu",
    # Input capture functions
    "get_click",
    "get_key",
    "get_mouse_position",
    "on_click_event",
    "on_key_event",
    # Input simulation functions
    "click",
    "move_mouse",
    "press_key",
    "hold_key",
    "release_key",
    "type_text",
    "send_keys",
    # Dialog functions
    "select_file",
    "select_folder",
    "save_file_dialog",
]
