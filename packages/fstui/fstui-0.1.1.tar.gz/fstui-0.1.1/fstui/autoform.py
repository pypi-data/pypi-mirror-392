#!/usr/bin/env python3
"""
Auto Form - Reusable Textual apps for Pydantic models.

Provides two main use cases:
1. create() - Create a new model instance from scratch
2. update() - Edit an existing model instance

These are the primary interfaces for working with Pydantic models in a TUI.
"""

from typing import TypeVar, Type, Optional, Callable
from pathlib import Path

from pydantic import BaseModel
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical, Container
from rich.console import Console

from .form_generator import PydanticFormGenerator


T = TypeVar("T", bound=BaseModel)


class AutoForm(App[Optional[T]]):
    """
    Generic Textual application for creating/editing Pydantic models.

    This is the base app that handles both create and update scenarios.
    Use the convenience functions create() and update() instead
    of instantiating this directly.

    Usage:
        # Create new
        app = AutoForm(UserModel)
        result = app.run()

        # Edit existing
        app = AutoForm(UserModel, existing_instance)
        result = app.run()
    """

    CSS = """
    Screen {
        align: center top;
    }
    
    #content-container {
        width: 100%;
        height: auto;
        margin: 1 2;
    }
    
    .section {
        border: solid $primary;
        padding: 1 2;
        margin-bottom: 1;
        height: auto;
    }
    
    .section-title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    
    .json-display {
        background: $panel;
        padding: 1;
        height: auto;
        min-height: 3;
        max-height: 15;
        overflow-y: auto;
    }
    
    .info-text {
        color: $text-muted;
        text-style: italic;
        margin-bottom: 1;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(
        self,
        model_class: Type[T],
        model_instance: Optional[T] = None,
        title: Optional[str] = None,
        show_original: bool = True,
        default_values: Optional[dict] = None,
        **kwargs,
    ):
        """
        Initialize the model form app.

        Args:
            model_class: The Pydantic model class to create/edit
            model_instance: Optional existing instance to edit (None for create)
            title: Custom title for the form (auto-generated if None)
            show_original: Whether to show original data when editing
            default_values: Optional dict with default values for form fields (for create mode)
        """
        super().__init__(**kwargs)
        self.model_class = model_class
        self.model_instance = model_instance
        self.show_original = show_original
        self.is_editing = model_instance is not None
        self.default_values = default_values or {}

        # Generate title
        if title:
            self.form_title = title
        else:
            action = "Edit" if self.is_editing else "Create"
            self.form_title = f"{action} {model_class.__name__}"

    def compose(self) -> ComposeResult:
        """Create the UI."""
        yield Header()

        with Vertical(id="content-container"):
            # Show original data if editing
            if self.is_editing and self.show_original and self.model_instance:
                with Container(classes="section"):
                    yield Static("📝 Current Data", classes="section-title")
                    yield Static(
                        "Editing existing record. Fields below are pre-filled with current values.",
                        classes="info-text",
                    )
                    # Display original data as JSON
                    json_str = self.model_instance.model_dump_json(indent=2)
                    yield Static(json_str, classes="json-display")

            # Form section
            with Container(classes="section"):
                icon = "✏️" if self.is_editing else "➕"
                yield Static(f"{icon} {self.form_title}", classes="section-title")

                # Create form with initial data
                initial_data = None
                if self.model_instance:
                    # If editing, use existing instance data
                    initial_data = self.model_instance.model_dump()
                elif self.default_values:
                    # If creating with defaults, use provided default values
                    initial_data = self.default_values

                yield PydanticFormGenerator(
                    self.model_class, initial_data=initial_data, id="model-form"
                )

        yield Footer()

    def on_pydantic_form_generator_submitted(
        self, message: PydanticFormGenerator.Submitted
    ) -> None:
        """Handle form submission."""
        self.exit(message.model_instance)

    def on_pydantic_form_generator_cancelled(
        self, message: PydanticFormGenerator.Cancelled
    ) -> None:
        """Handle form cancellation."""
        self.exit(None)


# Convenience functions for common use cases


def create(
    model_class: Type[T],
    title: Optional[str] = None,
    default_values: Optional[dict] = None,
    on_success: Optional[Callable[[T], None]] = None,
    on_cancel: Optional[Callable[[], None]] = None,
) -> Optional[T]:
    """
    Create a new Pydantic model instance via interactive form.

    This is the main function to use when you need users to fill out
    a form to create a new model instance.

    Args:
        model_class: The Pydantic model class to create
        title: Custom title for the form
        default_values: Optional dict with default values for form fields
        on_success: Callback function called with the created instance
        on_cancel: Callback function called when user cancels

    Returns:
        The created model instance, or None if cancelled

    Example:
        ```python
        from pydantic import BaseModel
        from fstui import create

        class User(BaseModel):
            name: str
            email: str
            age: int

        # Create new user with defaults
        new_user = create(User, default_values={
            "name": "Alice",
            "age": 25
        })

        # Create new user without defaults
        new_user = create(User)
        if new_user:
            print(f"Created: {new_user.name}")
            # Save to database, etc.
        ```
    """
    app = AutoForm(
        model_class=model_class,
        model_instance=None,
        title=title,
        show_original=False,
        default_values=default_values,  # Pass default values to the app
    )

    result = app.run()

    if result and on_success:
        on_success(result)
    elif not result and on_cancel:
        on_cancel()

    return result


def update(
    model_instance: T,
    title: Optional[str] = None,
    show_original: bool = True,
    on_success: Optional[Callable[[T, T], None]] = None,
    on_cancel: Optional[Callable[[], None]] = None,
) -> Optional[T]:
    """
    Update an existing Pydantic model instance via interactive form.

    This is the main function to use when you need users to edit
    existing data. The form will be pre-filled with current values.

    Args:
        model_instance: The existing model instance to edit
        title: Custom title for the form
        show_original: Whether to show current data before the form
        on_success: Callback with (original, updated) instances
        on_cancel: Callback function called when user cancels

    Returns:
        The updated model instance, or None if cancelled

    Example:
        ```python
        from fstui import update

        # Load existing user
        user = User(name="Alice", email="alice@example.com", age=30)

        # Edit user
        updated = update(user)
        if updated:
            print(f"Updated: {updated.name}")
            # Save changes to database, etc.
        ```
    """
    model_class = type(model_instance)

    app = AutoForm(
        model_class=model_class,
        model_instance=model_instance,
        title=title,
        show_original=show_original,
    )

    result = app.run()

    if result and on_success:
        on_success(model_instance, result)
    elif not result and on_cancel:
        on_cancel()

    return result


def show_diff(original: BaseModel, updated: BaseModel) -> None:
    """
    Display differences between two model instances.

    Utility function to show what changed after an update.

    Args:
        original: The original model instance
        updated: The updated model instance

    Example:
        ```python
        updated = prompt_edit(user)
        if updated:
            show_diff(user, updated)
        ```
    """
    console = Console()

    original_data = original.model_dump()
    updated_data = updated.model_dump()

    changes_found = False

    console.print("\n[bold yellow]📊 Changes:[/bold yellow]")

    for field_name in original_data.keys():
        original_value = original_data[field_name]
        updated_value = updated_data[field_name]

        if original_value != updated_value:
            changes_found = True
            console.print(f"  [cyan]{field_name}:[/cyan]")
            console.print(f"    [red]- {original_value}[/red]")
            console.print(f"    [green]+ {updated_value}[/green]")

    if not changes_found:
        console.print("  [dim]No changes made[/dim]")


# Example usage
if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))

    from examples.example_models import TaskModel, PriorityLevel
    from datetime import date

    console = Console()

    # Demo 1: Create new model
    console.print("\n[bold blue]Demo 1: Create New Task[/bold blue]\n")
    new_task = create(TaskModel, title="Create New Task")

    if new_task:
        console.print("\n[bold green]✅ Task Created![/bold green]")
        console.print(new_task.model_dump_json(indent=2))
    else:
        console.print("\n[yellow]❌ Cancelled[/yellow]")

    # Demo 2: Update existing model
    console.print("\n[bold blue]Demo 2: Update Existing Task[/bold blue]\n")

    existing_task = TaskModel(
        title="Review Pull Request #123",
        description="Review the new feature implementation",
        priority=PriorityLevel.HIGH,
        due_date=date(2025, 10, 25),
        tags=["review", "urgent", "backend"],
        estimated_hours=3.5,
        is_completed=False,
    )

    console.print("[bold]Original Task:[/bold]")
    console.print(existing_task.model_dump_json(indent=2))

    updated_task = update(existing_task, title="Edit Task")

    if updated_task:
        console.print("\n[bold green]✅ Task Updated![/bold green]")
        console.print(updated_task.model_dump_json(indent=2))

        # Show what changed
        show_diff(existing_task, updated_task)
    else:
        console.print("\n[yellow]❌ Cancelled[/yellow]")
