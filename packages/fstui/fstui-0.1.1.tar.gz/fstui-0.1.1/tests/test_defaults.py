#!/usr/bin/env python3
"""
Test script for default values functionality in create_model.
"""

from enum import Enum
from datetime import date
from typing import Optional
from pydantic import BaseModel

from fstui import create_model


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    due_date: Optional[date] = None
    is_completed: bool = False


def test_create_with_defaults():
    """Test creating a task with default values."""
    print("🧪 Testing create_model with default values...")

    # Test with default values
    defaults = {
        "title": "Sample Task",
        "description": "This is a pre-filled task",
        "priority": Priority.HIGH,
        "due_date": date(2024, 12, 31),
        "is_completed": False,
    }

    print("\n📝 Creating task with these defaults:")
    for key, value in defaults.items():
        print(f"  {key}: {value}")

    task = create_model(
        Task, title="Create Task with Defaults", default_values=defaults
    )

    if task:
        print("\n✅ Task created successfully!")
        print(f"   Title: {task.title}")
        print(f"   Description: {task.description}")
        print(f"   Priority: {task.priority}")
        print(f"   Due Date: {task.due_date}")
        print(f"   Completed: {task.is_completed}")
    else:
        print("\n❌ Task creation was cancelled")


def test_create_without_defaults():
    """Test creating a task without default values."""
    print("\n\n🧪 Testing create_model without default values...")

    task = create_model(Task, title="Create Task (No Defaults)")

    if task:
        print("\n✅ Task created successfully!")
        print(f"   Title: {task.title}")
        print(f"   Description: {task.description}")
        print(f"   Priority: {task.priority}")
        print(f"   Due Date: {task.due_date}")
        print(f"   Completed: {task.is_completed}")
    else:
        print("\n❌ Task creation was cancelled")


def main():
    """Main test function."""
    print("🚀 Testing default values functionality in create_model\n")
    print("=" * 60)

    while True:
        print("\nChoose a test:")
        print("1. Create task with default values")
        print("2. Create task without default values")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            test_create_with_defaults()
        elif choice == "2":
            test_create_without_defaults()
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
