from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="alyios-windows",
    version="0.1.0",
    description="Windows-specific utilities for interactive console, input capture/simulation, and crisp DPI-aware file dialogs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alyios",
    url="https://github.com/Alyios/alyios-windows",
    project_urls={
    },
    license="MIT",
    packages=find_packages(),
    package_data={
        'AlyiosWindowsFunctions': ['DialogHelper.exe', 'DialogHelper.cs', 'app.manifest', 'build_helper.ps1'],
    },
    include_package_data=True,
    install_requires=[
        # No external dependencies - uses native C# helper for crisp dialogs
    ],
    python_requires=">=3.7",
    keywords=[
        "windows", "console", "input", "dialog", "mouse", "keyboard",
        "automation", "gui", "ctypes", "windows-api", "file-dialog",
        "interactive", "terminal", "cli"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: System :: Systems Administration",
    ],
)
