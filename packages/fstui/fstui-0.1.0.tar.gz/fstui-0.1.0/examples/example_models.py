"""
Example Pydantic models for testing the form generator.
"""

from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PriorityLevel(Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class UserProfile(BaseModel):
    """Simple user profile model."""

    name: str = Field(..., description="Full name of the user")
    email: str = Field(..., description="Email address")
    age: Optional[int] = Field(None, description="Age in years", ge=0, le=150)
    is_active: bool = Field(True, description="Account active status")


class TaskModel(BaseModel):
    """Task management model with various field types."""

    title: str = Field(..., description="Task title", min_length=1)
    description: Optional[str] = Field(
        None,
        description="Detailed description (Markdown supported)",
        json_schema_extra={"format": "markdown"},
    )
    priority: PriorityLevel = Field(PriorityLevel.MEDIUM, description="Task priority")
    due_date: Optional[date] = Field(None, description="Due date (YYYY-MM-DD)")
    tags: Optional[list[str]] = Field(None, description="Tags (comma-separated)")
    estimated_hours: Optional[float] = Field(
        None, description="Estimated hours to complete", ge=0
    )
    is_completed: bool = Field(False, description="Completion status")


class ProductModel(BaseModel):
    """Product information model."""

    name: str = Field(..., description="Product name")
    sku: str = Field(..., description="Stock keeping unit code")
    price: float = Field(..., description="Price in USD", gt=0)
    stock: int = Field(0, description="Available stock quantity", ge=0)
    is_available: bool = Field(True, description="Available for purchase")
    release_date: Optional[date] = Field(None, description="Product release date")
    categories: Optional[list[str]] = Field(None, description="Product categories")


class PersonalInfo(BaseModel):
    """Comprehensive personal information form."""

    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    birth_date: Optional[date] = Field(None, description="Date of birth")
    country: str = Field("USA", description="Country of residence")
    subscribe_newsletter: bool = Field(False, description="Subscribe to newsletter")


class BlogPost(BaseModel):
    """Blog post with Markdown content."""

    title: str = Field(..., description="Post title", min_length=1, max_length=200)
    slug: str = Field(..., description="URL slug", pattern=r"^[a-z0-9-]+$")
    content: str = Field(
        ...,
        description="Post content (Markdown)",
        json_schema_extra={"format": "markdown"},
    )
    excerpt: Optional[str] = Field(None, description="Short excerpt", max_length=500)
    tags: Optional[list[str]] = Field(None, description="Tags (comma-separated)")
    published: bool = Field(False, description="Published status")
    publish_date: Optional[date] = Field(None, description="Publish date (YYYY-MM-DD)")


class CodeReview(BaseModel):
    """Code review with markdown notes."""

    reviewer: str = Field(..., description="Reviewer name")
    file_path: str = Field(..., description="File path being reviewed")
    notes: str = Field(
        ...,
        description="Review notes (Markdown)",
        json_schema_extra={"format": "markdown"},
    )
    severity: str = Field("info", description="Severity level")
    approved: bool = Field(False, description="Approved status")
