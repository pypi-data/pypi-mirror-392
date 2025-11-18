"""
FSTUI - Command Line Interface
Interactive TUI tools for file packaging and form generation.
"""

from pathlib import Path
import typer
from rich.console import Console

# Import from fstui package
from fstui import FilePackager
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

# CLI Application
cli = typer.Typer(
    name="fstui",
    help="📦 FSTUI - Interactive file packager and form generator",
    add_completion=False,
)
console = Console()


# File Packager App
class PackagerApp(App):
    """Main application for the file packager."""

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, source_dir: str = ".") -> None:
        super().__init__()
        self.source_dir = Path(source_dir).resolve()

    def compose(self) -> ComposeResult:
        yield Header()
        yield FilePackager(self.source_dir)
        yield Footer()

    def on_file_packager_packaged(self, message: FilePackager.Packaged) -> None:
        if message.archive_path:
            print(f"\n{'=' * 60}")
            print("✅ ARCHIVE CREATED")
            print(f"{'=' * 60}")
            print(f"📦 Archive: {message.archive_path}")
            print(f"💾 Size: {message.archive_path.stat().st_size:,} bytes")
            print(f"{'=' * 60}\n")
        self.exit(message.archive_path)


@cli.command()
def package(source_dir: str = typer.Argument(".", help="Source directory")) -> None:
    """📦 Create ZIP/TAR.GZ archives with custom structures."""
    console.print("\n[bold blue]📦 FSTUI Packager[/bold blue]")
    console.print(f"Source: [cyan]{Path(source_dir).resolve()}[/cyan]\n")

    app = PackagerApp(source_dir)
    archive_path = app.run()

    if archive_path:
        console.print(f"\n[green]✨ Success! {archive_path}[/green]")


@cli.command()
def form(example: str = typer.Option(None, "--example", "-e")) -> None:
    """📝 Generate forms from Pydantic models."""
    if example:
        from examples.form_app import (
            example_user_profile,
            example_task,
            example_product,
            example_personal_info,
            example_blog_post,
            example_code_review,
        )

        examples_map = {
            "user": example_user_profile,
            "task": example_task,
            "product": example_product,
            "personal": example_personal_info,
            "blog": example_blog_post,
            "review": example_code_review,
        }

        if example in examples_map:
            console.print(f"\n[cyan]Running: {example}[/cyan]\n")
            result = examples_map[example]()
            if result:
                console.print("[green]✓ Completed![/green]")
                console.print_json(result.model_dump_json())
        else:
            console.print(f"[red]Unknown: {example}[/red]")
    else:
        console.print("[yellow]Use --example <name>[/yellow]")


@cli.command()
def edit(example: str) -> None:
    """✏️ Edit existing Pydantic models."""
    from examples.edit_demo import (
        demo_edit_task,
        demo_edit_blog,
        demo_create_new,
        demo_edit_workflow,
    )

    demos = {
        "task": demo_edit_task,
        "blog": demo_edit_blog,
        "personal": demo_create_new,
        "workflow": demo_edit_workflow,
    }

    if example in demos:
        console.print(f"\n[cyan]✏️ {example}[/cyan]\n")
        demos[example]()
    else:
        console.print(f"[red]Unknown: {example}[/red]")


@cli.command()
def version() -> None:
    """Show version."""
    from fstui import __version__

    console.print(f"[bold blue]FSTUI[/bold blue] v{__version__}")


if __name__ == "__main__":
    cli()
