#!/usr/bin/env python3
"""Test list field parsing in form generator."""

from typing import Optional
from pydantic import BaseModel, Field


class TestModel(BaseModel):
    """Test model with list field."""

    tags: Optional[list[str]] = Field(None, description="Tags (comma-separated)")
    required_tags: list[str] = Field(description="Required tags")


def test_list_parsing():
    """Test that list fields are parsed correctly."""
    from typing import get_origin, get_args

    # Test field info
    for field_name, field_info in TestModel.model_fields.items():
        field_type = field_info.annotation
        print(f"\n{field_name}:")
        print(f"  Type: {field_type}")
        print(f"  Origin: {get_origin(field_type)}")
        print(f"  Args: {get_args(field_type)}")

        # Simulate unwrapping
        origin = get_origin(field_type)
        args = get_args(field_type)

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

        actual_origin = get_origin(actual_type)
        print(f"  Actual type: {actual_type}")
        print(f"  Actual origin: {actual_origin}")
        print(f"  Is list? {actual_origin is list}")


def test_value_parsing():
    """Test parsing comma-separated values."""
    test_inputs = [
        "a, b, c",
        "a,b,c",
        "tag1, tag2",
        "  spaces  ,  around  ",
        "",
    ]

    print("\n" + "=" * 50)
    print("Testing value parsing:")
    print("=" * 50)

    for input_str in test_inputs:
        value = input_str.strip()
        if not value:
            result = None
        else:
            result = [item.strip() for item in value.split(",") if item.strip()]
        print(f"Input: {input_str!r:30} -> Result: {result}")


if __name__ == "__main__":
    test_list_parsing()
    test_value_parsing()

    print("\n" + "=" * 50)
    print("Testing actual model creation:")
    print("=" * 50)

    # Test with valid data
    try:
        model = TestModel(tags=["a", "b", "c"], required_tags=["x", "y"])
        print(f"✅ Success: {model}")
        print(f"   tags: {model.tags}")
        print(f"   required_tags: {model.required_tags}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test with None for optional
    try:
        model = TestModel(tags=None, required_tags=["x", "y"])
        print(f"✅ Success with None: {model}")
    except Exception as e:
        print(f"❌ Error: {e}")
