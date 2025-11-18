"""
FSTUI - Filesystem and Form UI Tools for Textual

A collection of interactive TUI components for:
1. File packaging (ZIP/TAR archives with custom structures)
2. Pydantic form generation (create/edit models interactively)

Public API:
-----------

File Packaging:
    FilePackager - Widget for creating file packages

Form Generation:
    PydanticFormGenerator - Widget for Pydantic model forms
    create() - Create new model instance
    update() - Edit existing model instance
    show_diff() - Display model changes

Quick Start:
-----------

File Packaging:
    ```python
    from fstui import FilePackager
    from textual.app import App

    class MyApp(App):
        def compose(self):
            yield FilePackager("/path/to/source")
    ```

Form Creation:
    ```python
    from fstui import create
    from pydantic import BaseModel

    class User(BaseModel):
        name: str
        email: str

    user = create(User)
    ```

Form Editing:
    ```python
    from fstui import update, show_diff

    existing_user = User(name="Alice", email="alice@example.com")
    updated = update(existing_user)

    if updated:
        show_diff(existing_user, updated)
    ```
"""

__version__ = "0.1.1"

# File packaging
from .packager import FilePackager

# Form generation
from .form_generator import PydanticFormGenerator
from .autoform import (
    create,
    update,
    show_diff,
    AutoForm,
)

__all__ = [
    # File packaging
    "FilePackager",
    # Form generation - Main API (New clean names)
    "create",
    "update",
    "show_diff",
    # Form generation - Advanced
    "PydanticFormGenerator",
    "AutoForm",
    # Version
    "__version__",
]
