#!/usr/bin/env python3
"""
Test script for the new simplified API: create() and update()
"""

from enum import Enum
from datetime import date
from typing import Optional
from pydantic import BaseModel

# Test new clean API
from fstui import create, update, show_diff


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


def test_new_api():
    """Test the new clean API."""
    print("🚀 Testing new clean API: create() and update()")
    print("=" * 50)

    # Test create with defaults
    print("\n1. Testing create() with defaults...")
    defaults = {
        "title": "Clean API Task",
        "description": "Testing the new simplified API",
        "priority": Priority.HIGH,
        "due_date": date(2025, 12, 31),
    }

    task = create(Task, title="Create with New API", default_values=defaults)

    if task:
        print(f"✅ Created: {task.title}")
        print(f"   Priority: {task.priority}")
        print(f"   Due Date: {task.due_date}")

        # Test update
        print("\n2. Testing update()...")
        updated = update(task, title="Edit with New API")

        if updated:
            print(f"✅ Updated: {updated.title}")
            show_diff(task, updated)
        else:
            print("❌ Update cancelled")

    else:
        print("❌ Create cancelled")


def test_backward_compatibility():
    """Test that old API still works."""
    print("\n\n🔄 Testing backward compatibility...")

    # Import old names
    from fstui import create_model, update_model, show_changes

    task = create_model(Task, title="Old API Test")

    if task:
        print(f"✅ Old API create_model() works: {task.title}")

        updated = update_model(task, title="Old API Edit")
        if updated:
            print(f"✅ Old API update_model() works: {updated.title}")
            show_changes(task, updated)
    else:
        print("❌ Old API test cancelled")


if __name__ == "__main__":
    while True:
        print("\nChoose a test:")
        print("1. Test new clean API (create, update)")
        print("2. Test backward compatibility (create_model, update_model)")
        print("3. Exit")

        choice = input("\nEnter choice (1-3): ").strip()

        if choice == "1":
            test_new_api()
        elif choice == "2":
            test_backward_compatibility()
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")
