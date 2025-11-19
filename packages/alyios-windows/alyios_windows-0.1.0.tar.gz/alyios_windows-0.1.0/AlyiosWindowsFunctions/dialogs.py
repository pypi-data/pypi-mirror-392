"""
Modern file and folder dialogs using DPI-aware C# helper executable
Provides crisp, native Windows 10/11 dialogs
"""

import subprocess
import os
from typing import Optional, List, Tuple
from pathlib import Path

# Path to the compiled dialog helper
_HELPER_EXE = Path(__file__).parent / "DialogHelper.exe"


def _ensure_helper_built():
    """Ensure the dialog helper executable exists"""
    if not _HELPER_EXE.exists():
        raise FileNotFoundError(
            f"DialogHelper.exe not found at {_HELPER_EXE}. "
            "Please run build_helper.ps1 to compile it."
        )


def select_file(
    title: str = "Select a file",
    initialdir: Optional[str] = None,
    filetypes: Optional[List[Tuple[str, str]]] = None,
    multiple: bool = False
) -> Optional[str]:
    """
    Open a modern Windows file selection dialog with crisp DPI scaling.

    Args:
        title: Dialog window title
        initialdir: Initial directory to open (defaults to current directory)
        filetypes: List of tuples for file type filters, e.g., [("Text files", "*.txt"), ("All files", "*.*")]
        multiple: If True, allows selecting multiple files

    Returns:
        Selected file path(s) - string if multiple=False, tuple of strings if multiple=True, or None if cancelled

    Examples:
        >>> filepath = select_file()
        >>> if filepath:
        ...     print(f"Selected: {filepath}")
        ... else:
        ...     print("Selection cancelled")
        >>>
        >>> files = select_file(title="Select files", multiple=True)
        >>> if files:
        ...     print(f"Selected {len(files)} files")
    """
    _ensure_helper_built()

    if initialdir is None:
        initialdir = os.getcwd()

    # Build filter string
    if filetypes:
        filter_parts = []
        for desc, pattern in filetypes:
            filter_parts.append(f"{desc} ({pattern})|{pattern}")
        filter_str = "|".join(filter_parts)
    else:
        filter_str = "All Files (*.*)|*.*"

    # Build command
    cmd = [str(_HELPER_EXE), "openfile", f"--title={title}", f"--initialdir={initialdir}",
           f"--filter={filter_str}"]

    if multiple:
        cmd.append("--multiple")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            if multiple:
                files = output.split('|')
                if files:
                    print(f"Selected {len(files)} file(s)")
                    return tuple(files)
            else:
                print(f"Selected: {output}")
                return output
        elif result.returncode == 2:
            print("File selection cancelled")
            return None
        else:
            print(f"Error: {result.stderr.strip()}")
            return None

    except subprocess.TimeoutExpired:
        print("Dialog timeout")
        return None
    except Exception as e:
        print(f"Error opening file dialog: {e}")
        return None


def select_folder(
    title: str = "Select a folder",
    initialdir: Optional[str] = None
) -> Optional[str]:
    """
    Open a modern Windows folder selection dialog with crisp DPI scaling.

    Args:
        title: Dialog window title
        initialdir: Initial directory to open (defaults to current directory)

    Returns:
        Selected folder path as string, or None if cancelled

    Example:
        >>> folder = select_folder(title="Choose output directory")
        >>> if folder:
        ...     print(f"Selected: {folder}")
        ... else:
        ...     print("Folder selection cancelled")
    """
    _ensure_helper_built()

    if initialdir is None:
        initialdir = os.getcwd()

    # Build command
    cmd = [str(_HELPER_EXE), "folder", f"--description={title}", f"--selectedpath={initialdir}"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"Selected folder: {output}")
            return output
        elif result.returncode == 2:
            print("Folder selection cancelled")
            return None
        else:
            print(f"Error: {result.stderr.strip()}")
            return None

    except subprocess.TimeoutExpired:
        print("Dialog timeout")
        return None
    except Exception as e:
        print(f"Error opening folder dialog: {e}")
        return None


def save_file_dialog(
    title: str = "Save file",
    initialdir: Optional[str] = None,
    initialfile: str = "",
    defaultextension: str = "",
    filetypes: Optional[List[Tuple[str, str]]] = None
) -> Optional[str]:
    """
    Open a modern Windows save file dialog with crisp DPI scaling.

    Args:
        title: Dialog window title
        initialdir: Initial directory to open (defaults to current directory)
        initialfile: Default filename
        defaultextension: Default file extension (e.g., ".txt")
        filetypes: List of tuples for file type filters

    Returns:
        Selected file path as string, or None if cancelled

    Example:
        >>> filepath = save_file_dialog(
        ...     title="Save Report",
        ...     initialfile="report.txt",
        ...     defaultextension=".txt",
        ...     filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        ... )
        >>> if filepath:
        ...     print(f"Save to: {filepath}")
        ... else:
        ...     print("Save cancelled")
    """
    _ensure_helper_built()

    if initialdir is None:
        initialdir = os.getcwd()

    # Build filter string
    if filetypes:
        filter_parts = []
        for desc, pattern in filetypes:
            filter_parts.append(f"{desc} ({pattern})|{pattern}")
        filter_str = "|".join(filter_parts)
    else:
        filter_str = "All Files (*.*)|*.*"

    # Remove leading dot from extension
    if defaultextension and defaultextension.startswith('.'):
        defaultextension = defaultextension[1:]

    # Build command
    cmd = [str(_HELPER_EXE), "savefile", f"--title={title}", f"--initialdir={initialdir}",
           f"--filename={initialfile}", f"--defaultext={defaultextension}", f"--filter={filter_str}"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"Save to: {output}")
            return output
        elif result.returncode == 2:
            print("Save cancelled")
            return None
        else:
            print(f"Error: {result.stderr.strip()}")
            return None

    except subprocess.TimeoutExpired:
        print("Dialog timeout")
        return None
    except Exception as e:
        print(f"Error opening save dialog: {e}")
        return None
