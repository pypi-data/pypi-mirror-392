"""
Mouse and keyboard input capture and simulation utilities using Windows API via ctypes
"""

import ctypes
from ctypes import wintypes
import time
import threading
from typing import Tuple, Optional, Callable

# Virtual key codes
VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_MBUTTON = 0x04

# Mouse event constants for mouse_event
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000

# Keyboard event constants
KEYEVENTF_KEYUP = 0x0002

# Virtual key codes for common keys
VK_CODES = {
    0x08: 'backspace', 0x09: 'tab', 0x0D: 'enter', 0x10: 'shift',
    0x11: 'ctrl', 0x12: 'alt', 0x1B: 'esc', 0x20: 'space',
    0x21: 'page_up', 0x22: 'page_down', 0x23: 'end', 0x24: 'home',
    0x25: 'left', 0x26: 'up', 0x27: 'right', 0x28: 'down',
    0x2D: 'insert', 0x2E: 'delete', 0x70: 'f1', 0x71: 'f2',
    0x72: 'f3', 0x73: 'f4', 0x74: 'f5', 0x75: 'f6',
    0x76: 'f7', 0x77: 'f8', 0x78: 'f9', 0x79: 'f10',
    0x7A: 'f11', 0x7B: 'f12',
}

# Windows structures
class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

# Windows API functions
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


def get_mouse_position() -> Tuple[int, int]:
    """
    Get the current mouse cursor position.

    Returns:
        Tuple of (x, y) coordinates

    Example:
        >>> x, y = get_mouse_position()
        >>> print(f"Mouse is at ({x}, {y})")
    """
    point = POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return (point.x, point.y)


def get_click(timeout: Optional[float] = None, verbose: bool = True) -> Tuple[int, int, str]:
    """
    Wait for and capture the next mouse click using polling.

    Args:
        timeout: Maximum time to wait in seconds (None for no timeout)
        verbose: If True, print a message indicating waiting for click

    Returns:
        Tuple of (x, y, button) where:
            - x, y are the click coordinates
            - button is the button name ('left', 'right', 'middle')

    Example:
        >>> print("Click anywhere on the screen...")
        >>> x, y, button = get_click()
        >>> print(f"Clicked at ({x}, {y}) with {button} button")
    """
    if verbose:
        print("Waiting for mouse click...")

    start_time = time.time()

    # Wait for all buttons to be released first
    while (user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000 or
           user32.GetAsyncKeyState(VK_RBUTTON) & 0x8000 or
           user32.GetAsyncKeyState(VK_MBUTTON) & 0x8000):
        time.sleep(0.01)
        if timeout and (time.time() - start_time) > timeout:
            raise TimeoutError("No click detected within timeout period")

    # Now wait for a button to be pressed
    while True:
        if timeout and (time.time() - start_time) > timeout:
            raise TimeoutError("No click detected within timeout period")

        # Check left button
        if user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
            x, y = get_mouse_position()
            return (x, y, 'left')

        # Check right button
        if user32.GetAsyncKeyState(VK_RBUTTON) & 0x8000:
            x, y = get_mouse_position()
            return (x, y, 'right')

        # Check middle button
        if user32.GetAsyncKeyState(VK_MBUTTON) & 0x8000:
            x, y = get_mouse_position()
            return (x, y, 'middle')

        time.sleep(0.01)


def get_key(timeout: Optional[float] = None, verbose: bool = True) -> str:
    """
    Wait for and capture the next keyboard key press using polling.

    Args:
        timeout: Maximum time to wait in seconds (None for no timeout)
        verbose: If True, print a message indicating waiting for key

    Returns:
        String representation of the pressed key

    Example:
        >>> print("Press any key...")
        >>> key = get_key()
        >>> print(f"You pressed: {key}")
    """
    if verbose:
        print("Waiting for key press...")

    start_time = time.time()

    # Wait for all keys to be released first
    time.sleep(0.1)

    # Poll for key presses
    while True:
        if timeout and (time.time() - start_time) > timeout:
            raise TimeoutError("No key press detected within timeout period")

        # Check all virtual key codes
        for vk_code in range(0x08, 0xFE):  # VK codes from 8 to 254
            if user32.GetAsyncKeyState(vk_code) & 0x8000:
                # Get key name
                if vk_code in VK_CODES:
                    key_name = VK_CODES[vk_code]
                elif 0x30 <= vk_code <= 0x39:  # Numbers 0-9
                    key_name = chr(vk_code)
                elif 0x41 <= vk_code <= 0x5A:  # Letters A-Z
                    key_name = chr(vk_code).lower()
                else:
                    key_name = f'key_{vk_code}'

                return key_name

        time.sleep(0.01)


class MouseListener:
    """Continuous mouse event listener using polling"""
    def __init__(self, callback: Callable[[int, int, str, bool], None]):
        self.callback = callback
        self.running = False
        self.thread = None
        self.prev_left = False
        self.prev_right = False
        self.prev_middle = False

    def _poll_loop(self):
        """Polling loop for mouse events"""
        while self.running:
            x, y = get_mouse_position()

            # Check left button
            left_pressed = bool(user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000)
            if left_pressed != self.prev_left:
                self.callback(x, y, 'left', left_pressed)
                self.prev_left = left_pressed

            # Check right button
            right_pressed = bool(user32.GetAsyncKeyState(VK_RBUTTON) & 0x8000)
            if right_pressed != self.prev_right:
                self.callback(x, y, 'right', right_pressed)
                self.prev_right = right_pressed

            # Check middle button
            middle_pressed = bool(user32.GetAsyncKeyState(VK_MBUTTON) & 0x8000)
            if middle_pressed != self.prev_middle:
                self.callback(x, y, 'middle', middle_pressed)
                self.prev_middle = middle_pressed

            time.sleep(0.01)

    def start(self):
        """Start listening for mouse events"""
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop listening for mouse events"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)


def on_click_event(callback: Callable[[int, int, str, bool], None]):
    """
    Register a callback function to be called on every mouse click.

    Args:
        callback: Function that takes (x, y, button, pressed) as arguments

    Returns:
        The listener object (call .stop() to stop listening)

    Example:
        >>> def handle_click(x, y, button, pressed):
        ...     if pressed:
        ...         print(f"Clicked at ({x}, {y})")
        >>>
        >>> listener = on_click_event(handle_click)
        >>> # ... do other work ...
        >>> listener.stop()  # Stop listening when done
    """
    listener = MouseListener(callback)
    listener.start()
    return listener


class KeyboardListener:
    """Continuous keyboard event listener using polling"""
    def __init__(self, callback: Callable[[str, bool], None]):
        self.callback = callback
        self.running = False
        self.thread = None
        self.prev_states = {}

    def _poll_loop(self):
        """Polling loop for keyboard events"""
        while self.running:
            # Check all virtual key codes
            for vk_code in range(0x08, 0xFE):
                pressed = bool(user32.GetAsyncKeyState(vk_code) & 0x8000)
                prev_pressed = self.prev_states.get(vk_code, False)

                if pressed != prev_pressed:
                    # Get key name
                    if vk_code in VK_CODES:
                        key_name = VK_CODES[vk_code]
                    elif 0x30 <= vk_code <= 0x39:  # Numbers 0-9
                        key_name = chr(vk_code)
                    elif 0x41 <= vk_code <= 0x5A:  # Letters A-Z
                        key_name = chr(vk_code).lower()
                    else:
                        key_name = f'key_{vk_code}'

                    self.callback(key_name, pressed)
                    self.prev_states[vk_code] = pressed

            time.sleep(0.01)

    def start(self):
        """Start listening for keyboard events"""
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop listening for keyboard events"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)


def on_key_event(callback: Callable[[str, bool], None]):
    """
    Register a callback function to be called on every key press/release.

    Args:
        callback: Function that takes (key, pressed) as arguments

    Returns:
        The listener object (call .stop() to stop listening)

    Example:
        >>> def handle_key(key, pressed):
        ...     if pressed:
        ...         print(f"Key pressed: {key}")
        >>>
        >>> listener = on_key_event(handle_key)
        >>> # ... do other work ...
        >>> listener.stop()  # Stop listening when done
    """
    listener = KeyboardListener(callback)
    listener.start()
    return listener


# ===== INPUT SIMULATION FUNCTIONS =====

def move_mouse(x: int, y: int):
    """
    Move the mouse cursor to the specified screen coordinates.

    Args:
        x: Target x-coordinate
        y: Target y-coordinate

    Example:
        >>> move_mouse(500, 300)
    """
    user32.SetCursorPos(x, y)


def click(x: int, y: int, button: str = 'left', clicks: int = 1, interval: float = 0.1):
    """
    Simulate a mouse click at the specified coordinates.

    Args:
        x: Target x-coordinate
        y: Target y-coordinate
        button: Mouse button to click ('left', 'right', or 'middle')
        clicks: Number of times to click (default: 1)
        interval: Delay between clicks in seconds (default: 0.1)

    Example:
        >>> # Single left click at (500, 300)
        >>> click(500, 300)
        >>>
        >>> # Double right-click
        >>> click(500, 300, button='right', clicks=2)
    """
    # Move mouse to target position
    move_mouse(x, y)
    time.sleep(0.05)  # Small delay to ensure mouse has moved

    # Determine which button events to use
    if button == 'left':
        down_event = MOUSEEVENTF_LEFTDOWN
        up_event = MOUSEEVENTF_LEFTUP
    elif button == 'right':
        down_event = MOUSEEVENTF_RIGHTDOWN
        up_event = MOUSEEVENTF_RIGHTUP
    elif button == 'middle':
        down_event = MOUSEEVENTF_MIDDLEDOWN
        up_event = MOUSEEVENTF_MIDDLEUP
    else:
        raise ValueError(f"Invalid button: {button}. Must be 'left', 'right', or 'middle'")

    # Perform the clicks
    for _ in range(clicks):
        user32.mouse_event(down_event, 0, 0, 0, 0)
        time.sleep(0.01)
        user32.mouse_event(up_event, 0, 0, 0, 0)
        if clicks > 1:
            time.sleep(interval)


def press_key(key: str):
    """
    Press and release a keyboard key.

    Args:
        key: The key to press (e.g., 'a', 'enter', 'f1', 'ctrl')

    Example:
        >>> press_key('enter')
        >>> press_key('a')
        >>> press_key('f5')
    """
    vk_code = _get_vk_code(key)
    user32.keybd_event(vk_code, 0, 0, 0)  # Key down
    time.sleep(0.01)
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)  # Key up


def hold_key(key: str):
    """
    Hold down a keyboard key (without releasing).

    Args:
        key: The key to hold down

    Example:
        >>> hold_key('shift')
        >>> press_key('a')  # Types 'A'
        >>> release_key('shift')
    """
    vk_code = _get_vk_code(key)
    user32.keybd_event(vk_code, 0, 0, 0)  # Key down


def release_key(key: str):
    """
    Release a held keyboard key.

    Args:
        key: The key to release

    Example:
        >>> hold_key('ctrl')
        >>> press_key('c')  # Ctrl+C
        >>> release_key('ctrl')
    """
    vk_code = _get_vk_code(key)
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)  # Key up


def type_text(text: str, interval: float = 0.01):
    """
    Type a string of text by simulating key presses.

    Args:
        text: The text to type
        interval: Delay between key presses in seconds (default: 0.01)

    Example:
        >>> type_text("Hello, World!")
    """
    for char in text:
        # Get the virtual key code for the character
        vk = user32.VkKeyScanW(ord(char))

        # Extract the virtual key code and shift state
        vk_code = vk & 0xFF
        shift_state = (vk >> 8) & 0xFF

        # Press shift if needed
        if shift_state & 1:  # Shift key required
            user32.keybd_event(0x10, 0, 0, 0)  # VK_SHIFT down
            time.sleep(0.01)

        # Press the key
        user32.keybd_event(vk_code, 0, 0, 0)  # Key down
        time.sleep(0.01)
        user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)  # Key up

        # Release shift if it was pressed
        if shift_state & 1:
            time.sleep(0.01)
            user32.keybd_event(0x10, 0, KEYEVENTF_KEYUP, 0)  # VK_SHIFT up

        time.sleep(interval)


def send_keys(keys: str):
    """
    Send a key combination (e.g., Ctrl+C, Alt+Tab).

    Args:
        keys: Key combination as a string (e.g., 'ctrl+c', 'alt+tab', 'ctrl+shift+esc')

    Example:
        >>> send_keys('ctrl+c')  # Copy
        >>> send_keys('ctrl+v')  # Paste
        >>> send_keys('alt+tab')  # Switch windows
        >>> send_keys('ctrl+shift+esc')  # Task Manager
    """
    # Parse the key combination
    key_parts = [k.strip().lower() for k in keys.split('+')]

    # Get VK codes for all keys
    vk_codes = [_get_vk_code(key) for key in key_parts]

    # Press all keys in order
    for vk in vk_codes:
        user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.01)

    # Release all keys in reverse order
    for vk in reversed(vk_codes):
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.01)


def _get_vk_code(key: str) -> int:
    """
    Get the virtual key code for a given key name.

    Args:
        key: Key name (e.g., 'a', 'enter', 'ctrl')

    Returns:
        Virtual key code

    Raises:
        ValueError: If the key name is not recognized
    """
    key = key.lower()

    # Special keys
    special_keys = {
        'backspace': 0x08, 'tab': 0x09, 'enter': 0x0D, 'shift': 0x10,
        'ctrl': 0x11, 'alt': 0x12, 'pause': 0x13, 'caps_lock': 0x14,
        'esc': 0x1B, 'space': 0x20, 'page_up': 0x21, 'page_down': 0x22,
        'end': 0x23, 'home': 0x24, 'left': 0x25, 'up': 0x26,
        'right': 0x27, 'down': 0x28, 'select': 0x29, 'print': 0x2A,
        'execute': 0x2B, 'print_screen': 0x2C, 'insert': 0x2D, 'delete': 0x2E,
        'help': 0x2F, 'win': 0x5B, 'f1': 0x70, 'f2': 0x71, 'f3': 0x72,
        'f4': 0x73, 'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
        'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
        'num_lock': 0x90, 'scroll_lock': 0x91,
    }

    if key in special_keys:
        return special_keys[key]

    # Single character (letter or number)
    if len(key) == 1:
        if key.isalpha():
            return ord(key.upper())
        elif key.isdigit():
            return ord(key)

    raise ValueError(f"Unknown key: {key}")
