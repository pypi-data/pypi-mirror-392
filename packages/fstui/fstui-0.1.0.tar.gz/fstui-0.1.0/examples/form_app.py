"""
Form Generator App - Test application for Pydantic form generation.
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container
from textual.screen import Screen
from rich.console import Console

from form_generator import PydanticFormGenerator
from example_models import UserProfile, TaskModel, ProductModel, PersonalInfo


console = Console()


class FormScreen(Screen):
    """Screen that displays a form for a Pydantic model."""

    CSS = """
    FormScreen {
        align: center middle;
    }
    
    FormScreen Container {
        width: 80;
        height: auto;
        max-height: 90%;
        background: $panel;
        border: solid $primary;
        padding: 2;
        overflow-y: auto;
    }
    
    FormScreen .form-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }
    """

    def __init__(self, model_class, name: str = None):
        super().__init__(name)
        self.model_class = model_class
        self.result = None

    def compose(self) -> ComposeResult:
        """Create the form screen layout."""
        yield Header()
        with Container():
            yield PydanticFormGenerator(self.model_class)
        yield Footer()

    def on_pydantic_form_generator_submitted(
        self, message: PydanticFormGenerator.Submitted
    ) -> None:
        """Handle form submission."""
        self.result = message.model_instance

        # Display result
        console.print("\n" + "=" * 60)
        console.print("[bold green]✅ Form Submitted Successfully![/bold green]")
        console.print("=" * 60)
        console.print(
            f"\n[bold cyan]Model Type:[/bold cyan] {type(message.model_instance).__name__}"
        )
        console.print("\n[bold yellow]Data:[/bold yellow]")
        console.print(message.model_instance.model_dump_json(indent=2))
        console.print("\n" + "=" * 60 + "\n")

        self.app.exit(message.model_instance)

    def on_pydantic_form_generator_cancelled(
        self, message: PydanticFormGenerator.Cancelled
    ) -> None:
        """Handle form cancellation."""
        console.print("\n[yellow]Form cancelled[/yellow]\n")
        self.app.exit(None)


class FormGeneratorApp(App):
    """Main application for testing form generation."""

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self, model_class):
        super().__init__()
        self.model_class = model_class

    def on_mount(self) -> None:
        """Push the form screen when app starts."""
        self.push_screen(FormScreen(self.model_class))


def run_form(model_class, initial_data: dict = None):
    """
    Run the form generator for a given Pydantic model.

    Args:
        model_class: The Pydantic BaseModel class
        initial_data: Optional dict of initial values

    Returns:
        The filled model instance or None if cancelled
    """
    app = FormGeneratorApp(model_class)
    return app.run()


# Example usage functions
def example_user_profile():
    """Example: User profile form."""
    console.print("[bold blue]📝 User Profile Form[/bold blue]\n")
    result = run_form(UserProfile)
    return result


def example_task():
    """Example: Task creation form."""
    console.print("[bold blue]✅ Task Creation Form[/bold blue]\n")
    result = run_form(TaskModel)
    return result


def example_product():
    """Example: Product information form."""
    console.print("[bold blue]📦 Product Form[/bold blue]\n")
    result = run_form(ProductModel)
    return result


def example_personal_info():
    """Example: Personal information form."""
    console.print("[bold blue]👤 Personal Information Form[/bold blue]\n")
    result = run_form(PersonalInfo)
    return result


def example_blog_post():
    """Example: Blog post with Markdown editor."""
    console.print("[bold blue]📝 Blog Post Form (with Markdown editor)[/bold blue]\n")
    from example_models import BlogPost

    result = run_form(BlogPost)
    return result


def example_code_review():
    """Example: Code review with Markdown notes."""
    console.print("[bold blue]🔍 Code Review Form (with Markdown notes)[/bold blue]\n")
    from example_models import CodeReview

    result = run_form(CodeReview)
    return result


if __name__ == "__main__":
    # Run a simple example
    example_user_profile()
