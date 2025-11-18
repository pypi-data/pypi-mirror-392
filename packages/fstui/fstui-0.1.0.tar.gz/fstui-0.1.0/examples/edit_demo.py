#!/usr/bin/env python3
"""
Demo: Creating and Editing Pydantic model instances
Shows how to use create() and update() functions.
"""

from datetime import date
from rich.console import Console

from fstui.autoform import create, update, show_diff
from example_models import TaskModel, BlogPost, PersonalInfo, PriorityLevel


def demo_edit_task():
    """Demo: Edit an existing task."""
    console = Console()

    # Create an existing task
    existing_task = TaskModel(
        title="Review Pull Request #123",
        description="Review the new feature implementation\n\n- Check code quality\n- Test functionality\n- Update docs",
        priority=PriorityLevel.HIGH,
        due_date=date(2025, 10, 25),
        tags=["review", "urgent", "backend"],
        estimated_hours=3.5,
        is_completed=False,
    )

    console.print("\n[bold blue]📝 Task Editor Demo[/bold blue]")
    console.print("[dim]Editing existing task...[/dim]\n")

    # Show original task
    console.print("[bold]Original Task:[/bold]")
    console.print(existing_task.model_dump_json(indent=2))
    console.print()

    # Launch editor using update()
    updated_task = update(existing_task, title="Edit Task")

    if updated_task:
        console.print("\n[bold green]✅ Task Updated![/bold green]\n")
        console.print("[bold]Updated Task:[/bold]")
        console.print(updated_task.model_dump_json(indent=2))

        # Show what changed
        show_diff(existing_task, updated_task)
    else:
        console.print("\n[yellow]❌ Edit cancelled[/yellow]")


def demo_edit_blog():
    """Demo: Edit a blog post with markdown content."""
    console = Console()

    # Create an existing blog post
    existing_post = BlogPost(
        title="Getting Started with Textual",
        content="""# Introduction

Textual is a **powerful** framework for building terminal user interfaces.

## Features

- Rich text rendering
- Reactive programming
- CSS-like styling
- Widget composition

## Example

```python
from textual.app import App

class MyApp(App):
    pass
```

Pretty cool, right?
""",
        author="Alice",
        tags=["textual", "python", "tui"],
        published_date=date(2025, 10, 1),
    )

    console.print("\n[bold blue]📝 Blog Post Editor Demo[/bold blue]")
    console.print("[dim]Editing existing blog post with Markdown...[/dim]\n")

    # Launch editor using update()
    updated_post = update(existing_post, title="Edit Blog Post")

    if updated_post:
        console.print("\n[bold green]✅ Blog Post Updated![/bold green]\n")
        console.print(f"[bold]Title:[/bold] {updated_post.title}")
        console.print(f"[bold]Author:[/bold] {updated_post.author}")
        console.print(f"[bold]Tags:[/bold] {', '.join(updated_post.tags or [])}")
        console.print("\n[bold]Content:[/bold]")
        console.print(updated_post.content)

        # Show changes
        show_diff(existing_post, updated_post)
    else:
        console.print("\n[yellow]❌ Edit cancelled[/yellow]")


def demo_create_new():
    """Demo: Create a new instance from scratch."""
    console = Console()

    console.print("\n[bold blue]📝 Create New Personal Info[/bold blue]")
    console.print("[dim]Creating a new record from scratch...[/dim]\n")

    # Launch creator using create()
    new_person = create(PersonalInfo, title="Create Personal Information")

    if new_person:
        console.print("\n[bold green]✅ Personal Info Created![/bold green]\n")
        console.print(new_person.model_dump_json(indent=2))
    else:
        console.print("\n[yellow]❌ Creation cancelled[/yellow]")


def demo_edit_workflow():
    """Demo: Complete edit workflow with validation."""
    console = Console()

    console.print("\n[bold blue]🔄 Complete Edit Workflow Demo[/bold blue]\n")

    # Step 1: Load existing data
    console.print("[bold]Step 1:[/bold] Load existing task")
    task = TaskModel(
        title="Bug Fix: Login Issue", priority=PriorityLevel.URGENT, is_completed=False
    )
    console.print(f"  Title: {task.title}")
    console.print(f"  Priority: {task.priority.value}")
    console.print(f"  Completed: {task.is_completed}")

    # Step 2: Edit
    console.print("\n[bold]Step 2:[/bold] Open editor...")

    # Define success callback
    def on_update_success(original, updated):
        console.print("\n[bold]Step 3:[/bold] Validate changes")
        if updated.is_completed and not original.is_completed:
            console.print("  [green]✓[/green] Task marked as completed!")

        console.print("\n[bold]Step 4:[/bold] Save changes")
        console.print("  [green]✓[/green] Changes saved successfully")

    updated = update(task, on_success=on_update_success)

    if updated:
        console.print("\n[bold green]✅ Workflow Complete![/bold green]")
        console.print(updated.model_dump_json(indent=2))
    else:
        console.print("\n[yellow]Workflow cancelled[/yellow]")


if __name__ == "__main__":
    import sys

    console = Console()

    demos = {
        "task": ("Edit a task", demo_edit_task),
        "blog": ("Edit a blog post with Markdown", demo_edit_blog),
        "create": ("Create new personal info", demo_create_new),
        "workflow": ("Complete edit workflow", demo_edit_workflow),
    }

    if len(sys.argv) > 1:
        demo_name = sys.argv[1]
        if demo_name in demos:
            _, demo_func = demos[demo_name]
            demo_func()
        else:
            console.print(f"[red]Unknown demo: {demo_name}[/red]")
            console.print("\n[bold]Available demos:[/bold]")
            for name, (desc, _) in demos.items():
                console.print(f"  [cyan]{name}[/cyan] - {desc}")
    else:
        console.print("[bold blue]🎯 Model Editor Demos[/bold blue]\n")
        console.print("Choose a demo to run:\n")
        for name, (desc, _) in demos.items():
            console.print(f"  [cyan]{name:12}[/cyan] - {desc}")
        console.print("\n[dim]Usage: python edit_demo.py <demo_name>[/dim]")
        console.print("[dim]Example: python edit_demo.py task[/dim]")
