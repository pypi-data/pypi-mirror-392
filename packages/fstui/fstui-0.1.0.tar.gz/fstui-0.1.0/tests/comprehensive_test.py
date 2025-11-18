#!/usr/bin/env python3
"""
Comprehensive test for the enhanced create_model function with default values.
"""

from enum import Enum
from datetime import date
from typing import Optional
from pydantic import BaseModel

from fstui import create_model


class Status(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class UserProfile(BaseModel):
    name: str
    email: str
    age: int
    is_active: bool = True
    skills: Optional[str] = None  # Will be treated as multiline text
    join_date: Optional[date] = None


class Article(BaseModel):
    title: str
    content: str
    status: Status = Status.DRAFT
    publish_date: Optional[date] = None
    view_count: int = 0


def test_comprehensive_defaults():
    """Test various field types with default values."""
    print("🧪 Testing comprehensive default values...")

    # Test UserProfile with defaults
    user_defaults = {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "age": 28,
        "is_active": True,
        "skills": "Python\nJavaScript\nSQL",
        "join_date": date.today(),
    }

    print("\n👤 Creating UserProfile with defaults:")
    for key, value in user_defaults.items():
        print(f"  {key}: {value}")

    user = create_model(UserProfile, title="用戶註冊", default_values=user_defaults)

    if user:
        print("\n✅ User created successfully!")
        print(f"   Name: {user.name}")
        print(f"   Email: {user.email}")
        print(f"   Age: {user.age}")
        print(f"   Active: {user.is_active}")
        print(f"   Skills: {repr(user.skills)}")
        print(f"   Join Date: {user.join_date}")
    else:
        print("\n❌ User creation was cancelled")


def test_partial_defaults():
    """Test with only some fields having defaults."""
    print("\n\n🧪 Testing partial default values...")

    # Only set some defaults
    article_defaults = {"title": "My First Article", "status": Status.DRAFT}

    print("\n📄 Creating Article with partial defaults:")
    for key, value in article_defaults.items():
        print(f"  {key}: {value}")

    article = create_model(Article, title="寫新文章", default_values=article_defaults)

    if article:
        print("\n✅ Article created successfully!")
        print(f"   Title: {article.title}")
        print(f"   Content: {article.content[:50]}...")
        print(f"   Status: {article.status}")
        print(f"   Publish Date: {article.publish_date}")
        print(f"   View Count: {article.view_count}")
    else:
        print("\n❌ Article creation was cancelled")


def test_backwards_compatibility():
    """Test that existing code without default_values still works."""
    print("\n\n🧪 Testing backwards compatibility...")

    user = create_model(UserProfile, title="註冊新用戶")

    if user:
        print("\n✅ Backwards compatibility confirmed!")
        print(f"   Created user: {user.name}")
    else:
        print("\n❌ Backwards compatibility test cancelled")


def main():
    """Main test function."""
    print("🚀 Comprehensive Testing of create_model with default_values")
    print("=" * 70)

    while True:
        print("\n\nChoose a test:")
        print("1. Test comprehensive defaults (UserProfile)")
        print("2. Test partial defaults (Article)")
        print("3. Test backwards compatibility")
        print("4. Run all tests")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            test_comprehensive_defaults()
        elif choice == "2":
            test_partial_defaults()
        elif choice == "3":
            test_backwards_compatibility()
        elif choice == "4":
            print("\n🏃 Running all tests...")
            test_comprehensive_defaults()
            test_partial_defaults()
            test_backwards_compatibility()
            print("\n🎉 All tests completed!")
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()
