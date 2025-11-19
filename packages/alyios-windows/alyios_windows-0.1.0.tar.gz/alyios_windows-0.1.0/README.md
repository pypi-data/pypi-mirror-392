# Alyios Windows Functions

A pure Python package for Windows-specific utilities with **zero external dependencies**. All functionality is implemented using native Python and Windows API via `ctypes`.

## Features

### 1. Interactive Console Interface
- Arrow key navigation (↑/↓)
- Visual selection indicators (→)
- Support for lists, dictionaries, and Enums
- Multi-selection with checkboxes
- Confirmation dialogs
- Text input with password masking

### 2. Mouse & Keyboard Input
**Capture:**
- Capture mouse clicks with position and button info
- Get current mouse position
- Capture keyboard key presses
- Continuous event listeners for both mouse and keyboard

**Simulation:**
- Simulate mouse clicks at specific coordinates
- Move mouse cursor programmatically
- Simulate keyboard key presses
- Type text automatically
- Send key combinations (Ctrl+C, Alt+Tab, etc.)

All implemented via Windows API

### 3. File Dialogs
- Native Windows file selection dialogs
- Folder selection dialogs
- Save file dialogs
- Support for file type filters
- Multi-file selection

## Installation

```bash
cd AlyiosWindowsFunctions
pip install -e .
```

## Usage Examples

### Console Interface

```python
from AlyiosWindowsFunctions import select_option, select_from_list, confirm

# Simple selection with arrow keys
choice = select_option(
    "Choose your favorite color:",
    ["Red", "Green", "Blue", "Yellow"]
)

# Using Enums
from enum import Enum

class Options(Enum):
    OPTION_A = "a"
    OPTION_B = "b"

choice = select_option("Select option:", Options)

# Multi-selection
items = select_from_list(
    "Choose items:",
    ["Item 1", "Item 2", "Item 3"],
    multi=True  # Use Space to toggle, Enter to confirm
)

# Yes/No confirmation
if confirm("Continue?", default=True):
    print("Confirmed!")
```

### Mouse & Keyboard Input

**Capture:**
```python
from AlyiosWindowsFunctions import get_click, get_key, get_mouse_position

# Get current mouse position
x, y = get_mouse_position()
print(f"Mouse at: ({x}, {y})")

# Wait for a mouse click
x, y, button = get_click()
print(f"Clicked at ({x}, {y}) with {button} button")

# Wait for a key press
key = get_key()
print(f"You pressed: {key}")

# Continuous event listener
from AlyiosWindowsFunctions import on_click_event

def handle_click(x, y, button, pressed):
    if pressed:
        print(f"Clicked at ({x}, {y})")

listener = on_click_event(handle_click)
# ... do work ...
listener.stop()
```

**Simulation:**
```python
from AlyiosWindowsFunctions import click, move_mouse, press_key, type_text, send_keys

# Simulate mouse click at coordinates
click(500, 300)  # Left click
click(500, 300, button='right')  # Right click
click(500, 300, clicks=2)  # Double-click

# Move mouse cursor
move_mouse(1000, 500)

# Simulate keyboard input
press_key('enter')
press_key('f5')

# Type text automatically
type_text("Hello, World!")

# Send key combinations
send_keys('ctrl+c')  # Copy
send_keys('ctrl+v')  # Paste
send_keys('alt+tab')  # Switch windows
```

### File Dialogs

```python
from AlyiosWindowsFunctions import select_file, select_folder, save_file_dialog

# Select a single file
filepath = select_file(
    title="Open File",
    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
)

# Select multiple files
files = select_file(title="Select Files", multiple=True)

# Select a folder
folder = select_folder(title="Choose Directory")

# Save file dialog
filepath = save_file_dialog(
    title="Save As",
    initialfile="document.txt",
    defaultextension=".txt",
    filetypes=[("Text files", "*.txt")]
)
```

## Technical Details

### No External Dependencies
This package uses **only**:
- Python standard library (`ctypes`, `getpass`, `os`, `sys`, `threading`, `time`, `enum`, `typing`)
- Windows API via `ctypes` (user32.dll, kernel32.dll, comdlg32.dll, shell32.dll, ole32.dll)

### Windows API Features Used
- **Console API**: For arrow key input and cursor control
- **Low-level hooks**: For mouse and keyboard capture
- **Common Dialogs**: For file/folder selection
- **Shell API**: For folder browsing

### Keyboard Controls

#### Single Selection:
- `↑/↓`: Navigate options
- `Enter` or `Space`: Select
- `Esc`: Cancel

#### Multi-Selection:
- `↑/↓`: Navigate options
- `Space`: Toggle selection
- `Enter`: Confirm selections
- `Esc`: Cancel

## Running the Demo

```bash
cd AlyiosWindowsFunctions
python example.py
```

The demo showcases all features with interactive examples.

## Requirements

- Python 3.7+
- Windows OS (uses Windows-specific APIs)

## License

MIT License
