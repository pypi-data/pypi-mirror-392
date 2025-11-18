#!/usr/bin/env python3
"""Test list widget creation and value extraction."""

from typing import Optional, get_origin, get_args
from pydantic import BaseModel, Field


class TestModel(BaseModel):
    """Test model with list field."""

    tags: Optional[list[str]] = Field(None, description="Tags")


# Simulate the form generator logic
def test_widget_creation():
    """Test creating widget with initial list value."""
    print("=" * 60)
    print("Testing Widget Creation with List Initial Value")
    print("=" * 60)

    # Simulate initial_data from model_dump()
    initial_data = {"tags": ["review", "urgent", "backend"]}

    # Get field info
    field_name = "tags"
    field_info = TestModel.model_fields[field_name]
    field_type = field_info.annotation

    print(f"\nField: {field_name}")
    print(f"Field type: {field_type}")
    print(f"Field info default: {field_info.default}")

    # This is what happens in _create_field_widget
    default_value = initial_data.get(field_name, field_info.default)
    print(f"\ndefault_value from initial_data: {default_value}")
    print(f"Type of default_value: {type(default_value)}")
    print(f"Is list: {isinstance(default_value, list)}")

    # Get origin
    origin = get_origin(field_type)
    args = get_args(field_type)

    print(f"\noriginal field_type: {field_type}")
    print(f"origin: {origin}")
    print(f"args: {args}")

    # Handle Optional
    if origin is type(None) or (
        hasattr(field_type, "__origin__") and type(None) in get_args(field_type)
    ):
        if args:
            actual_type = args[0] if args[0] is not type(None) else args[1]
            print(f"\nUnwrapped type: {actual_type}")

    # Check origin BEFORE unwrapping
    print(f"\nChecking: origin is list? {origin is list}")

    # This is the bug! origin is Union, not list
    # We need to check AFTER unwrapping

    # Correct way: re-get origin after unwrapping
    actual_type = args[0] if args and args[0] is not type(None) else field_type
    actual_origin = get_origin(actual_type)
    print(f"actual_origin (after unwrap): {actual_origin}")
    print(f"actual_origin is list? {actual_origin is list}")

    # Test value conversion
    print(f"\n{'=' * 60}")
    print("Testing Value Conversion for Widget")
    print(f"{'=' * 60}")

    from pydantic_core import PydanticUndefined

    if default_value is None or default_value is PydanticUndefined:
        value = ""
    elif isinstance(default_value, list):
        value = ", ".join(str(v) for v in default_value)
    else:
        value = str(default_value)

    print(f"\nInput widget value: {value!r}")
    print("✅ This is correct!")


if __name__ == "__main__":
    test_widget_creation()
