"""
Interactive console interface using Windows Console API via ctypes
Supports arrow key navigation with visual selection
"""

import ctypes
from ctypes import wintypes
from enum import Enum
from typing import List, Union, Optional
import sys
import os

# Windows Console API constants
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
ENABLE_ECHO_INPUT = 0x0004
ENABLE_LINE_INPUT = 0x0002
ENABLE_PROCESSED_INPUT = 0x0001
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

# Key event constants
KEY_EVENT = 0x0001
VK_UP = 0x26
VK_DOWN = 0x28
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
VK_SPACE = 0x20

# Console structures
class COORD(ctypes.Structure):
    _fields_ = [("X", wintypes.SHORT), ("Y", wintypes.SHORT)]

class KEY_EVENT_RECORD(ctypes.Structure):
    class _uChar(ctypes.Union):
        _fields_ = [
            ("UnicodeChar", wintypes.WCHAR),
            ("AsciiChar", wintypes.CHAR)
        ]
    _fields_ = [
        ("bKeyDown", wintypes.BOOL),
        ("wRepeatCount", wintypes.WORD),
        ("wVirtualKeyCode", wintypes.WORD),
        ("wVirtualScanCode", wintypes.WORD),
        ("uChar", _uChar),
        ("dwControlKeyState", wintypes.DWORD)
    ]

class INPUT_RECORD(ctypes.Structure):
    class _Event(ctypes.Union):
        _fields_ = [("KeyEvent", KEY_EVENT_RECORD)]
    _fields_ = [
        ("EventType", wintypes.WORD),
        ("Event", _Event)
    ]

class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", wintypes.WORD),
        ("srWindow", wintypes.SMALL_RECT),
        ("dwMaximumWindowSize", COORD)
    ]

# Windows API functions
kernel32 = ctypes.windll.kernel32
GetStdHandle = kernel32.GetStdHandle
ReadConsoleInputW = kernel32.ReadConsoleInputW
GetConsoleMode = kernel32.GetConsoleMode
SetConsoleMode = kernel32.SetConsoleMode
WriteConsoleW = kernel32.WriteConsoleW


def _enable_vt_mode():
    """Enable Virtual Terminal processing for ANSI escape codes"""
    hOut = GetStdHandle(STD_OUTPUT_HANDLE)
    mode = wintypes.DWORD()
    GetConsoleMode(hOut, ctypes.byref(mode))
    mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
    SetConsoleMode(hOut, mode)


def _get_key_event():
    """Read a key event from console input"""
    hConsole = GetStdHandle(STD_INPUT_HANDLE)

    # Save current console mode
    old_mode = wintypes.DWORD()
    GetConsoleMode(hConsole, ctypes.byref(old_mode))

    # Disable line input and echo
    new_mode = old_mode.value & ~(ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT)
    SetConsoleMode(hConsole, new_mode)

    try:
        while True:
            input_record = INPUT_RECORD()
            events_read = wintypes.DWORD()

            if ReadConsoleInputW(hConsole, ctypes.byref(input_record), 1, ctypes.byref(events_read)):
                if input_record.EventType == KEY_EVENT:
                    key_event = input_record.Event.KeyEvent
                    if key_event.bKeyDown:
                        return key_event
    finally:
        # Restore console mode
        SetConsoleMode(hConsole, old_mode)


def _render_menu(options: List[str], selected_idx: int, selected_items: set = None):
    """Render menu and return to start position"""
    # Move cursor up to overwrite previous menu
    if hasattr(_render_menu, 'last_line_count'):
        for _ in range(_render_menu.last_line_count):
            sys.stdout.write('\033[F')  # Move cursor up
            sys.stdout.write('\033[K')  # Clear line

    lines = []
    for idx, option in enumerate(options):
        if selected_items is not None:
            checkbox = "[X]" if idx in selected_items else "[ ]"
            arrow = "→" if idx == selected_idx else " "
            lines.append(f"  {arrow} {checkbox} {option}")
        else:
            if idx == selected_idx:
                lines.append(f"  → {option}")
            else:
                lines.append(f"    {option}")

    for line in lines:
        print(line)

    _render_menu.last_line_count = len(lines)


def select_option(
    message: str,
    choices: Union[List[str], List[dict], type],
    default: Optional[str] = None
) -> str:
    """
    Display an interactive selection menu with arrow key navigation.

    Args:
        message: The prompt message to display
        choices: List of options (can be list of strings, list of dicts, or Enum class)
        default: Default selected option

    Returns:
        The selected option as a string

    Controls:
        - Up/Down arrows: Navigate
        - Enter/Space: Select
        - Esc: Cancel (returns first option)

    Examples:
        >>> choice = select_option("Select a color:", ["Red", "Green", "Blue"])
        >>> class Colors(Enum):
        ...     RED = "red"
        >>> choice = select_option("Select a color:", Colors)
    """
    _enable_vt_mode()

    print(f"\n{message}")
    print("(Use arrow keys to navigate, Enter to select)\n")

    # Parse choices
    options = []
    values = []

    if isinstance(choices, type) and issubclass(choices, Enum):
        for item in choices:
            options.append(item.name)
            values.append(item.value)
    elif choices and isinstance(choices[0], dict):
        for choice_dict in choices:
            name = choice_dict.get('name', str(choice_dict.get('value', '')))
            value = choice_dict.get('value', name)
            options.append(name)
            values.append(value)
    else:
        options = list(choices)
        values = list(choices)

    # Find default index
    selected_idx = 0
    if default:
        for i, val in enumerate(values):
            if val == default:
                selected_idx = i
                break

    # Reset line count tracking
    _render_menu.last_line_count = 0

    # Display initial menu
    _render_menu(options, selected_idx)

    while True:
        key_event = _get_key_event()
        vk_code = key_event.wVirtualKeyCode

        if vk_code == VK_UP:
            selected_idx = (selected_idx - 1) % len(options)
            _render_menu(options, selected_idx)
        elif vk_code == VK_DOWN:
            selected_idx = (selected_idx + 1) % len(options)
            _render_menu(options, selected_idx)
        elif vk_code in (VK_RETURN, VK_SPACE):
            print(f"\nSelected: {options[selected_idx]}\n")
            return values[selected_idx]
        elif vk_code == VK_ESCAPE:
            print(f"\nCancelled\n")
            return values[0]


def select_from_list(
    message: str,
    choices: List[str],
    multi: bool = False
) -> Union[str, List[str]]:
    """
    Select one or multiple items from a list using arrow keys.

    Args:
        message: The prompt message to display
        choices: List of options to choose from
        multi: If True, allows multiple selections (use Space to toggle, Enter to confirm)

    Returns:
        Selected option(s) - single string if multi=False, list if multi=True

    Controls (multi=True):
        - Up/Down arrows: Navigate
        - Space: Toggle selection
        - Enter: Confirm selections
        - Esc: Cancel

    Examples:
        >>> choice = select_from_list("Pick a fruit:", ["Apple", "Banana", "Orange"])
        >>> choices = select_from_list("Pick toppings:", ["Cheese", "Pepperoni"], multi=True)
    """
    if not multi:
        return select_option(message, choices)

    _enable_vt_mode()

    print(f"\n{message}")
    print("(Use arrows to navigate, Space to toggle, Enter to confirm)\n")

    selected_idx = 0
    selected_items = set()

    # Reset line count tracking
    _render_menu.last_line_count = 0

    # Display initial menu
    _render_menu(choices, selected_idx, selected_items)

    while True:
        key_event = _get_key_event()
        vk_code = key_event.wVirtualKeyCode

        if vk_code == VK_UP:
            selected_idx = (selected_idx - 1) % len(choices)
            _render_menu(choices, selected_idx, selected_items)
        elif vk_code == VK_DOWN:
            selected_idx = (selected_idx + 1) % len(choices)
            _render_menu(choices, selected_idx, selected_items)
        elif vk_code == VK_SPACE:
            if selected_idx in selected_items:
                selected_items.remove(selected_idx)
            else:
                selected_items.add(selected_idx)
            _render_menu(choices, selected_idx, selected_items)
        elif vk_code == VK_RETURN:
            result = [choices[i] for i in sorted(selected_items)]
            print(f"\nSelected: {', '.join(result) if result else 'None'}\n")
            return result
        elif vk_code == VK_ESCAPE:
            print(f"\nCancelled\n")
            return []


def confirm(message: str, default: bool = False) -> bool:
    """
    Display a yes/no confirmation prompt with arrow key selection.

    Args:
        message: The question to ask
        default: Default answer (True for yes, False for no)

    Returns:
        True if user confirms, False otherwise

    Example:
        >>> if confirm("Do you want to continue?"):
        ...     print("Continuing...")
    """
    choices = ["Yes", "No"]
    default_choice = "Yes" if default else "No"
    result = select_option(message, choices, default_choice)
    return result == "Yes"


def get_text_input(message: str, default: str = "", password: bool = False) -> str:
    """
    Get text input from the user.

    Args:
        message: The prompt message
        default: Default value
        password: If True, input will be hidden (for passwords)

    Returns:
        The user's input as a string

    Examples:
        >>> name = get_text_input("Enter your name:")
        >>> password = get_text_input("Enter password:", password=True)
    """
    import getpass

    if password:
        return getpass.getpass(f"{message}: ") or default
    else:
        default_hint = f" [{default}]" if default else ""
        result = input(f"{message}{default_hint}: ").strip()
        return result if result else default


def display_menu(title: str, options: dict):
    """
    Display a menu with arrow key navigation and return the selected value.

    Args:
        title: Menu title
        options: Dictionary mapping display names to values

    Returns:
        The value associated with the selected option

    Example:
        >>> menu = {"Open File": "open", "Save File": "save", "Exit": "exit"}
        >>> action = display_menu("Main Menu", menu)
    """
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print('=' * 50)

    choices = [{"name": name, "value": value} for name, value in options.items()]
    return select_option("", choices)
