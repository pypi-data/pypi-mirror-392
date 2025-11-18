# FSTUI - Filesystem and Form UI Tools

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Textual](https://img.shields.io/badge/textual-TUI-green.svg)](https://github.com/Textualize/textual)

Interactive TUI (Terminal User Interface) tools for:
1. **File Packaging** - Create ZIP/TAR archives with custom directory structures
2. **Form Generation** - Auto-generate forms from Pydantic models

## 📦 Installation

```bash
# Clone and install
git clone <repository>
cd fstui
uv venv
uv pip install -e .
```

## 🚀 Quick Start

### File Packaging

Create custom archives with drag-and-drop style operations:

```bash
# Package files interactively
uv run fstui package /path/to/source
```

**Features:**
- Dual-panel interface (source | destination)
- Add files/folders (`a`)
- Create folders (`n`)
- Rename items (`r`)
- Delete items (`d`)
- Export as ZIP or TAR.GZ

### Form Generation

#### Create New Models

```python
from fstui import create_model
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int

# Interactive form
user = create_model(User)
if user:
    print(f"Created: {user.name}")
```

#### Edit Existing Models

```python
from fstui import update_model, show_changes

# Load existing data
user = User(name="Alice", email="alice@example.com", age=30)

# Edit interactively
updated = update_model(user)
if updated:
    show_changes(user, updated)
```

#### Run Examples

```bash
# Form examples
uv run fstui form --example task
uv run fstui form --example blog

# Edit examples
uv run fstui edit task
uv run fstui edit blog
```

## 📚 Project Structure

```
fstui/
├── fstui/              # Core package
│   ├── __init__.py     # Public API
│   ├── packager.py     # File packaging widget
│   ├── form_generator.py  # Form generation widget
│   └── model_app.py    # create_model/update_model functions
├── examples/           # Example models and demos
│   ├── example_models.py
│   ├── form_app.py
│   └── edit_demo.py
├── tests/              # Test files
│   ├── test_list_parsing.py
│   └── test_list_widget.py
├── docs/               # Documentation
│   ├── MODEL_APP_API.md
│   ├── QUICKSTART.md
│   └── ...
├── main.py             # CLI entry point
└── README.md           # This file
```

## 🎯 API Reference

### File Packaging

```python
from fstui import FilePackager
from textual.app import App

class MyApp(App):
    def compose(self):
        yield FilePackager("/path/to/source")

app = MyApp()
app.run()
```

### Form Generation - Main API

```python
from fstui import create_model, update_model, show_changes

# Create
new_instance = create_model(ModelClass)

# Update
updated_instance = update_model(existing_instance)

# Show changes
show_changes(original, updated)
```

### Form Generation - Advanced

```python
from fstui import PydanticFormGenerator, ModelFormApp

# Custom form widget
form = PydanticFormGenerator(ModelClass, initial_data={...})

# Custom app
app = ModelFormApp(ModelClass, model_instance=existing)
result = app.run()
```

## 📖 Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started quickly
- **[Model App API](docs/MODEL_APP_API.md)** - Complete API reference
- **[Form Features](docs/NEW_FEATURES.md)** - New features and testing

## 🔧 Supported Field Types

| Type | Widget | Notes |
|------|--------|-------|
| `str` | Input | TextArea for long text |
| `int`, `float` | Input | Numeric validation |
| `bool` | Switch | Toggle on/off |
| `Enum` | Select | Dropdown menu |
| `date` | Input | YYYY-MM-DD format |
| `list[T]` | Input | Comma-separated |
| `Optional[T]` | Any | Allow blank |

**Markdown Support:** Fields named `description`, `content`, `notes` or with `json_schema_extra={"format": "markdown"}` use a TextArea widget.

## 💡 Examples

### Task Management

```python
from enum import Enum
from pydantic import BaseModel
from fstui import create_model

class Priority(Enum):
    LOW = "low"
    HIGH = "high"

class Task(BaseModel):
    title: str
    priority: Priority
    completed: bool = False

task = create_model(Task)
```

### Blog Post Editor

```python
from datetime import date
from pydantic import BaseModel, Field
from fstui import update_model

class BlogPost(BaseModel):
    title: str
    content: str = Field(..., json_schema_extra={"format": "markdown"})
    published_date: date

post = BlogPost(title="Hello", content="# Welcome\n\nHello world!", published_date=date.today())
updated = update_model(post)
```

## 🐛 Known Issues

All major bugs have been fixed:
- ✅ Enum select values
- ✅ PydanticUndefined handling
- ✅ List field parsing
- ✅ Optional[list[T]] support

See [docs/FORM_FIXES.md](docs/FORM_FIXES.md) for details.

## 🤝 Contributing

Contributions welcome! Please check the project structure and follow existing patterns.

## 📄 License

[Add license information]

## 🙏 Acknowledgments

Built with:
- [Textual](https://github.com/Textualize/textual) - TUI framework
- [Pydantic](https://github.com/pydantic/pydantic) - Data validation
- [Typer](https://github.com/tiangolo/typer) - CLI framework
- [Rich](https://github.com/Textualize/rich) - Terminal formatting
