"""
Pydantic Form Generator for Textual
Automatically generate Textual forms from Pydantic v2 BaseModel classes.
"""

from typing import Type, Any, get_origin, get_args
from datetime import date
from enum import Enum

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Input, Select, Switch, Static, Button, Label, TextArea
from textual.containers import Vertical, Horizontal
from textual.message import Message


class PydanticFormGenerator(Widget):
    """
    A Textual widget that generates a form from a Pydantic BaseModel.

    Usage:
        class UserModel(BaseModel):
            name: str
            age: int
            email: str

        form = PydanticFormGenerator(UserModel)
        result = await form.get_model()  # Returns filled UserModel instance
    """

    DEFAULT_CSS = """
    PydanticFormGenerator {
        height: auto;
        padding: 1;
    }
    
    PydanticFormGenerator .field-container {
        height: auto;
        margin: 1 0;
    }
    
    PydanticFormGenerator .field-label {
        width: 100%;
        margin-bottom: 1;
        color: $accent;
    }
    
    PydanticFormGenerator .field-input {
        width: 100%;
    }
    
    PydanticFormGenerator .field-textarea {
        width: 100%;
        height: 10;
        border: solid $accent;
    }
    
    PydanticFormGenerator .field-description {
        width: 100%;
        color: $text-muted;
        text-style: italic;
        margin-top: 1;
    }
    
    PydanticFormGenerator .field-error {
        width: 100%;
        color: $error;
        margin-top: 1;
    }
    
    PydanticFormGenerator .form-buttons {
        height: auto;
        margin-top: 2;
        align: center middle;
    }
    
    PydanticFormGenerator Button {
        margin: 0 1;
    }
    """

    class Submitted(Message):
        """Posted when form is submitted with valid data."""

        def __init__(self, model_instance: BaseModel) -> None:
            super().__init__()
            self.model_instance = model_instance

    class Cancelled(Message):
        """Posted when form is cancelled."""

        pass

    def __init__(
        self,
        model_class: Type[BaseModel],
        initial_data: dict[str, Any] | None = None,
        **kwargs,
    ) -> None:
        """
        Initialize the form generator.

        Args:
            model_class: The Pydantic BaseModel class to generate form for
            initial_data: Optional dict of initial field values
        """
        super().__init__(**kwargs)
        self.model_class = model_class
        self.initial_data = initial_data or {}
        self.field_widgets: dict[str, Widget] = {}
        self.error_labels: dict[str, Static] = {}

    def compose(self) -> ComposeResult:
        """Generate form fields based on model schema."""
        yield Static(f"📝 {self.model_class.__name__} Form", classes="form-title")

        # Generate field for each model field
        for field_name, field_info in self.model_class.model_fields.items():
            yield from self._create_field_widget(field_name, field_info)

        # Form buttons
        with Horizontal(classes="form-buttons"):
            yield Button("Submit", variant="primary", id="submit-btn")
            yield Button("Cancel", variant="default", id="cancel-btn")

    def _create_field_widget(
        self, field_name: str, field_info: FieldInfo
    ) -> ComposeResult:
        """
        Create appropriate widget for a field based on its type.

        Args:
            field_name: Name of the field
            field_info: Pydantic FieldInfo object
        """
        with Vertical(classes="field-container"):
            # Field label
            label_text = field_info.title or field_name.replace("_", " ").title()
            required_marker = "" if field_info.is_required() else " (optional)"
            yield Label(f"{label_text}{required_marker}", classes="field-label")

            # Get field type
            field_type = field_info.annotation
            default_value = self.initial_data.get(field_name, field_info.default)

            # Create appropriate input widget
            widget = self._create_input_widget(
                field_name, field_type, default_value, field_info
            )

            if widget:
                self.field_widgets[field_name] = widget
                yield widget

            # Field description
            if field_info.description:
                yield Static(field_info.description, classes="field-description")

            # Error label (hidden by default)
            error_label = Static("", classes="field-error")
            error_label.display = False
            self.error_labels[field_name] = error_label
            yield error_label

    def _create_input_widget(
        self,
        field_name: str,
        field_type: Type,
        default_value: Any,
        field_info: FieldInfo,
    ) -> Widget | None:
        """
        Create the appropriate input widget based on field type.

        Supports:
        - str: Input
        - int, float: Input with numeric validation
        - bool: Switch
        - Enum: Select dropdown
        - date, datetime: Input with date format
        - list: Input (comma-separated)
        """
        # Get origin type for generic types (List, Optional, etc.)
        origin = get_origin(field_type)
        args = get_args(field_type)

        # Handle Optional types (Union[X, None])
        if origin is type(None) or (
            hasattr(field_type, "__origin__") and type(None) in get_args(field_type)
        ):
            # Extract the actual type from Optional
            if args:
                field_type = (
                    args[0]
                    if args[0] is not type(None)
                    else args[1]
                    if len(args) > 1
                    else str
                )
                # Re-evaluate origin and args after unwrapping Optional
                origin = get_origin(field_type)
                args = get_args(field_type)

        # String input
        if issubclass(field_type, str):
            if default_value is None or default_value is PydanticUndefined:
                value = ""
            else:
                value = str(default_value)

            # Check if this should be a TextArea (markdown/long text)
            # Use TextArea if:
            # 1. Field has json_schema_extra with format="markdown"
            # 2. Field name contains "description", "content", "notes", "body"
            use_textarea = False

            if field_info.json_schema_extra:
                if isinstance(field_info.json_schema_extra, dict):
                    if field_info.json_schema_extra.get("format") == "markdown":
                        use_textarea = True
                    elif field_info.json_schema_extra.get("widget") == "textarea":
                        use_textarea = True

            # Auto-detect based on field name
            if field_name.lower() in (
                "description",
                "content",
                "notes",
                "body",
                "text",
                "markdown",
            ):
                use_textarea = True

            if use_textarea:
                return TextArea(
                    text=value,
                    language="markdown",
                    theme="monokai",
                    classes="field-textarea",
                    id=f"input-{field_name}",
                )
            else:
                return Input(
                    value=value,
                    placeholder=f"Enter {field_name}",
                    classes="field-input",
                    id=f"input-{field_name}",
                )

        # Integer input
        elif issubclass(field_type, int):
            if default_value is None or default_value is PydanticUndefined:
                value = ""
            else:
                value = str(default_value)
            return Input(
                value=value,
                placeholder="Enter number",
                classes="field-input",
                id=f"input-{field_name}",
                type="integer",
            )

        # Float input
        elif issubclass(field_type, float):
            if default_value is None or default_value is PydanticUndefined:
                value = ""
            else:
                value = str(default_value)
            return Input(
                value=value,
                placeholder="Enter decimal number",
                classes="field-input",
                id=f"input-{field_name}",
                type="number",
            )

        # Boolean switch
        elif issubclass(field_type, bool):
            if default_value is None or default_value is PydanticUndefined:
                value = False
            else:
                value = bool(default_value)
            return Switch(value=value, id=f"input-{field_name}")

        # Enum select
        elif isinstance(field_type, type) and issubclass(field_type, Enum):
            # Options format: (prompt/label, value) - prompt is displayed, value is what gets stored
            options = [(member.name, member.value) for member in field_type]
            # Handle default value properly
            if default_value is not None and default_value is not PydanticUndefined:
                # If default is Enum member, get its value for Select
                select_value = (
                    default_value.value
                    if isinstance(default_value, Enum)
                    else default_value
                )
            else:
                select_value = Select.BLANK

            return Select(
                options=options,
                value=select_value,
                allow_blank=not field_info.is_required(),
                classes="field-input",
                id=f"input-{field_name}",
            )

        # Date input
        elif field_type is date or field_type == date:
            if default_value is None or default_value is PydanticUndefined:
                value = ""
            else:
                value = default_value.isoformat()
            return Input(
                value=value,
                placeholder="YYYY-MM-DD",
                classes="field-input",
                id=f"input-{field_name}",
            )

        # List input (comma-separated)
        elif origin is list:
            if default_value is None or default_value is PydanticUndefined:
                value = ""
            elif isinstance(default_value, list):
                # It's already a list, join it properly
                value = ", ".join(str(v) for v in default_value)
            else:
                # It's something else (maybe a string?), just use as-is
                value = str(default_value)
            return Input(
                value=value,
                placeholder="Enter values separated by commas",
                classes="field-input",
                id=f"input-{field_name}",
            )

        # Default: string input
        else:
            if default_value is None or default_value is PydanticUndefined:
                value = ""
            else:
                value = str(default_value)
            return Input(
                value=value,
                placeholder=f"Enter {field_name}",
                classes="field-input",
                id=f"input-{field_name}",
            )

    def _get_field_value(self, field_name: str, field_type: Type) -> Any:
        """Extract and convert field value from widget."""
        widget = self.field_widgets.get(field_name)
        if not widget:
            return None

        # Get origin for generic types
        origin = get_origin(field_type)
        args = get_args(field_type)

        # Handle Optional (Union[X, None])
        actual_type = field_type
        if origin is type(None) or (
            hasattr(field_type, "__origin__") and type(None) in get_args(field_type)
        ):
            if args:
                actual_type = (
                    args[0]
                    if args[0] is not type(None)
                    else (args[1] if len(args) > 1 else str)
                )

        # Re-evaluate origin and args for the actual type (after unwrapping Optional)
        actual_origin = get_origin(actual_type)
        get_args(actual_type)

        # Switch (bool)
        if isinstance(widget, Switch):
            return widget.value

        # Select (Enum)
        elif isinstance(widget, Select):
            selected_value = widget.value
            # If blank or empty, return None
            if selected_value == Select.BLANK or not selected_value:
                return None
            # Find the enum member by name
            if isinstance(actual_type, type) and issubclass(actual_type, Enum):
                for member in actual_type:
                    if member.name == selected_value:
                        return member
            return selected_value

        # TextArea (for markdown/long text)
        elif isinstance(widget, TextArea):
            value = widget.text.strip()
            return value if value else None

        # Input fields
        elif isinstance(widget, Input):
            value = widget.value.strip()

            if not value:
                return None

            # Convert based on type
            if issubclass(actual_type, int):
                return int(value)
            elif issubclass(actual_type, float):
                return float(value)
            elif issubclass(actual_type, date):
                return date.fromisoformat(value)
            elif actual_origin is list:
                # Parse comma-separated list
                return [item.strip() for item in value.split(",") if item.strip()]
            else:
                return value

        return None

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "submit-btn":
            await self._submit_form()
        elif event.button.id == "cancel-btn":
            self.post_message(self.Cancelled())

    async def _submit_form(self) -> None:
        """Collect form data and create model instance."""
        # Clear previous errors
        for error_label in self.error_labels.values():
            error_label.display = False
            error_label.update("")

        # Collect field values
        form_data = {}
        for field_name, field_info in self.model_class.model_fields.items():
            try:
                value = self._get_field_value(field_name, field_info.annotation)
                if value is not None:
                    form_data[field_name] = value
            except (ValueError, TypeError) as e:
                # Show error on field
                if field_name in self.error_labels:
                    self.error_labels[field_name].update(f"❌ {str(e)}")
                    self.error_labels[field_name].display = True
                return

        # Try to create model instance
        try:
            model_instance = self.model_class(**form_data)
            self.post_message(self.Submitted(model_instance))
        except Exception as e:
            # Show validation errors
            error_msg = str(e)
            # Try to parse pydantic validation errors
            if hasattr(e, "errors"):
                for error in e.errors():
                    field_name = error["loc"][0] if error["loc"] else None
                    if field_name and field_name in self.error_labels:
                        self.error_labels[field_name].update(f"❌ {error['msg']}")
                        self.error_labels[field_name].display = True
            else:
                # Generic error - show on first field
                if self.error_labels:
                    first_label = next(iter(self.error_labels.values()))
                    first_label.update(f"❌ {error_msg}")
                    first_label.display = True

    async def get_model(self) -> BaseModel | None:
        """
        Convenience method to run form and get result.
        Returns the model instance or None if cancelled.
        """
        result = None

        def on_submitted(message: PydanticFormGenerator.Submitted) -> None:
            nonlocal result
            result = message.model_instance

        self.on(PydanticFormGenerator.Submitted, on_submitted)

        return result
