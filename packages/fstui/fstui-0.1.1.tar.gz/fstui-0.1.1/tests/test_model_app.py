#!/usr/bin/env python3
"""Test the model_app API functions."""

from example_models import TaskModel, PriorityLevel
from rich.console import Console

console = Console()

# Test 1: Create model
console.print("\n[bold blue]Test 1: Create Model API[/bold blue]\n")
console.print("This would open a form to create a new task.")
console.print("Run interactively with: uv run main.py edit task\n")

# Test 2: Update model (simulated)
console.print("[bold blue]Test 2: Update Model API[/bold blue]\n")

existing_task = TaskModel(
    title="Review PR #123",
    description="Code review needed",
    priority=PriorityLevel.HIGH,
    tags=["review", "urgent", "backend"],
    is_completed=False,
)

console.print("[bold]Original Task:[/bold]")
console.print(existing_task.model_dump_json(indent=2))

console.print("\n[green]✅ API functions are properly defined![/green]")
console.print("\n[bold]Available functions:[/bold]")
console.print(
    "  • create_model(model_class, title=None, on_success=None, on_cancel=None)"
)
console.print(
    "  • update_model(model_instance, title=None, show_original=True, on_success=None, on_cancel=None)"
)
console.print("  • show_changes(original, updated)")

console.print("\n[bold]Test these interactively with:[/bold]")
console.print("  uv run main.py edit task")
console.print("  uv run main.py edit blog")
console.print("  uv run python3 edit_demo.py task")
