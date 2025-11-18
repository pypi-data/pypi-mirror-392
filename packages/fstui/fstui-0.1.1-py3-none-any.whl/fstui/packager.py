"""
FSTUI Packager - Interactive file packaging component.

A Textual widget for creating file packages with custom directory structures.
Provides a dual-panel interface for intuitive file organization and archiving.

Features:
- Browse source directory (left panel)
- Build package structure (right panel)
- Create folders, rename items, add/remove files
- Export as ZIP or TAR.GZ archives
"""

from pathlib import Path
from typing import Dict, Optional, Set
import shutil
import tempfile
import tarfile
import zipfile
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Container, VerticalScroll
from textual.widgets import DirectoryTree, Tree, Button, Static, Label, Input
from textual.widget import Widget
from textual.message import Message
from textual.widgets.tree import TreeNode
from textual.binding import Binding


class FilePackager(Widget):
    """Interactive file packager with dual-panel interface for creating archives."""

    BINDINGS = [
        Binding("a", "add_selected", "Add to Package", show=True),
        Binding("d", "remove_selected", "Remove from Package", show=True),
        Binding("c", "clear_dest", "Clear Package", show=True),
        Binding("n", "new_folder", "New Folder in Package", show=True),
        Binding("r", "rename_selected", "Rename", show=True),
    ]

    DEFAULT_CSS = """
    FilePackager {
        height: 100%;
        layout: vertical;
    }
    
    FilePackager .header-info {
        height: auto;
        padding: 1;
        background: $boost;
        border-bottom: solid $primary;
    }
    
    FilePackager .main-panels {
        height: 1fr;
        layout: horizontal;
    }
    
    FilePackager .panel {
        width: 50%;
        height: 100%;
        border: solid $accent;
        padding: 1;
    }
    
    FilePackager .panel-title {
        height: auto;
        padding: 0 0 1 0;
        text-style: bold;
    }
    
    FilePackager .tree-scroll {
        height: 1fr;
        border: solid $primary;
    }
    
    FilePackager .controls {
        height: auto;
        padding: 1;
        border-top: solid $accent;
    }
    
    FilePackager .button-row {
        height: auto;
        layout: horizontal;
        padding: 1 0;
    }
    
    FilePackager Button {
        margin: 0 1;
    }
    
    FilePackager Input {
        margin: 1 0;
    }
    
    FilePackager .rename-input {
        border: solid $warning;
    }
    
    FilePackager .stats {
        height: auto;
        padding: 1 0;
        color: $text-muted;
    }
    """

    class Packaged(Message):
        """Message sent when packaging is complete."""

        def __init__(self, archive_path: Path | None) -> None:
            self.archive_path = archive_path
            super().__init__()

    def __init__(
        self,
        source_dir: Path,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the improved file organizer.

        Args:
            source_dir: Source directory to browse
            name: The name of the widget
            id: The ID of the widget
            classes: CSS classes for the widget
        """
        super().__init__(name=name, id=id, classes=classes)
        self.source_dir = Path(source_dir).resolve()
        # Destination structure: path -> (is_dir, source_path)
        self.dest_structure: Dict[Path, tuple[bool, Path]] = {}
        # Map tree node IDs to paths for removal
        self.node_to_path: Dict[str, Path] = {}
        # Track which paths are expanded
        self.expanded_paths: Set[Path] = set()
        self.temp_dir: Optional[Path] = None
        self.archive_format = "zip"  # or "tar"

    def compose(self) -> ComposeResult:
        """Compose the organizer widget."""
        # Header info
        with Container(classes="header-info"):
            yield Label(f"📂 Source: {self.source_dir}")
            yield Label(
                "💡 Tip: Tab to switch | 'a' add | 'd' remove | 'n' new folder | 'r' rename | 'c' clear | 'q' quit"
            )
            yield Static("", id="stats_display", classes="stats")

        # Main panels
        with Horizontal(classes="main-panels"):
            # Left panel - Source directory
            with Vertical(classes="panel"):
                yield Label(
                    "📁 Source Directory (Select and press 'a' to add)",
                    classes="panel-title",
                )
                with VerticalScroll(classes="tree-scroll"):
                    yield DirectoryTree(str(self.source_dir), id="source_tree")

            # Right panel - Destination package
            with Vertical(classes="panel"):
                yield Label(
                    "📦 Package Contents (Select and press 'd' to remove)",
                    classes="panel-title",
                )
                with VerticalScroll(classes="tree-scroll"):
                    yield Tree("📦 Package Root", id="dest_tree")

        # Controls
        with Container(classes="controls"):
            yield Label("⚙️ Package Settings:")
            yield Input(
                placeholder="Rename selected item (press Enter to confirm)",
                id="rename_input",
                classes="rename-input",
            )
            yield Input(
                placeholder="Archive name (default: package_YYYYMMDD_HHMMSS)",
                id="archive_name_input",
            )

            with Horizontal(classes="button-row"):
                yield Button("🗜️ Create ZIP", variant="primary", id="create_zip_btn")
                yield Button("🗜️ Create TAR.GZ", variant="primary", id="create_tar_btn")
                yield Button("🗑️ Clear Package", variant="warning", id="clear_btn")
                yield Button("❌ Cancel", variant="error", id="cancel_btn")

    def on_mount(self) -> None:
        """Handle mount event."""
        tree = self.query_one("#source_tree", DirectoryTree)
        tree.show_root = True
        self._update_stats()

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        """Track when a node is expanded in the destination tree."""
        # Check if this is the destination tree by checking the control
        try:
            tree = self.query_one("#dest_tree", Tree)
            if event.node.tree == tree:
                node_id = str(id(event.node))
                if node_id in self.node_to_path:
                    self.expanded_paths.add(self.node_to_path[node_id])
        except Exception:
            pass

    def on_tree_node_collapsed(self, event: Tree.NodeCollapsed) -> None:
        """Track when a node is collapsed in the destination tree."""
        # Check if this is the destination tree by checking the control
        try:
            tree = self.query_one("#dest_tree", Tree)
            if event.node.tree == tree:
                node_id = str(id(event.node))
                if node_id in self.node_to_path:
                    path = self.node_to_path[node_id]
                    self.expanded_paths.discard(path)
        except Exception:
            pass

    def _update_stats(self) -> None:
        """Update statistics display."""
        stats = self.query_one("#stats_display", Static)
        file_count = sum(1 for is_dir, _ in self.dest_structure.values() if not is_dir)
        dir_count = sum(1 for is_dir, _ in self.dest_structure.values() if is_dir)
        stats.update(f"📊 Package: {file_count} files, {dir_count} folders")

    def _update_dest_tree(self) -> None:
        """Update the destination tree display."""
        tree = self.query_one("#dest_tree", Tree)

        # Save currently expanded paths before clearing
        # We iterate through all existing mappings to preserve expansion state
        # (No need to walk the tree since we track expanded_paths separately)

        tree.clear()
        tree.root.expand()
        self.node_to_path.clear()

        if not self.dest_structure:
            tree.root.add_leaf("(Empty - Add files from left panel)")
            return

        # Build tree structure
        tree_nodes: Dict[Path, TreeNode] = {Path("."): tree.root}

        # Sort: directories first, then files
        sorted_items = sorted(
            self.dest_structure.items(),
            key=lambda x: (not x[1][0], str(x[0])),  # dirs first, then by path
        )

        for dest_path, (is_dir, source_path) in sorted_items:
            # Create parent directories if needed
            current = Path(".")
            for part in dest_path.parts[:-1]:
                current = current / part
                if current not in tree_nodes:
                    parent_node = tree_nodes[
                        current.parent if current.parent != current else Path(".")
                    ]
                    # Check if this path should be expanded
                    should_expand = current in self.expanded_paths
                    new_node = parent_node.add(f"📁 {part}", expand=should_expand)
                    tree_nodes[current] = new_node
                    # Store the path for this node
                    self.node_to_path[str(id(new_node))] = current

            # Add file or directory
            parent_path = (
                dest_path.parent if dest_path.parent != Path(".") else Path(".")
            )
            parent_node = tree_nodes.get(parent_path, tree.root)

            icon = "📁" if is_dir else "📄"
            label = f"{icon} {dest_path.name}"

            if is_dir:
                # Check if this path should be expanded
                should_expand = dest_path in self.expanded_paths
                new_node = parent_node.add(label, expand=should_expand)
                tree_nodes[dest_path] = new_node
                self.node_to_path[str(id(new_node))] = dest_path
            else:
                new_node = parent_node.add_leaf(label)
                self.node_to_path[str(id(new_node))] = dest_path

        self._update_stats()

    def action_add_selected(self) -> None:
        """Add selected item from source to destination."""
        tree = self.query_one("#source_tree", DirectoryTree)
        if tree.cursor_node and tree.cursor_node.data:
            source_path = tree.cursor_node.data.path
            # Get the current destination folder (where to add)
            dest_base = self._get_current_dest_folder()
            self._add_to_destination(source_path, dest_base)

    def action_new_folder(self) -> None:
        """Create a new folder in the destination package."""
        # Get the current destination folder
        dest_base = self._get_current_dest_folder()

        # Generate a default folder name
        folder_num = 1
        while True:
            new_folder_name = f"new_folder_{folder_num}"
            new_folder_path = (
                dest_base / new_folder_name
                if dest_base != Path(".")
                else Path(new_folder_name)
            )
            if new_folder_path not in self.dest_structure:
                break
            folder_num += 1

        # Create a dummy source path (this folder doesn't exist in source)
        self.dest_structure[new_folder_path] = (True, Path("<virtual>"))
        self.expanded_paths.add(new_folder_path)
        self._update_dest_tree()
        self.notify(f"✓ Created folder: {new_folder_path}")

    def action_rename_selected(self) -> None:
        """Start renaming the selected item in the destination tree."""
        dest_tree = self.query_one("#dest_tree", Tree)

        if not dest_tree.cursor_node or dest_tree.cursor_node == dest_tree.root:
            self.notify("⚠️ No item selected to rename", severity="warning")
            return

        # Get the path for the selected node
        node_id = str(id(dest_tree.cursor_node))
        if node_id not in self.node_to_path:
            self.notify("⚠️ Cannot rename this item", severity="warning")
            return

        selected_path = self.node_to_path[node_id]

        # Focus the rename input and pre-fill with current name
        rename_input = self.query_one("#rename_input", Input)
        rename_input.value = selected_path.name
        rename_input.focus()
        self.notify(f"✏️ Renaming: {selected_path.name} (press Enter to confirm)")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submissions."""
        if event.input.id == "rename_input":
            self._perform_rename(event.value)
            event.input.value = ""

    def _perform_rename(self, new_name: str) -> None:
        """Perform the actual rename operation."""
        if not new_name or not new_name.strip():
            self.notify("⚠️ Name cannot be empty", severity="warning")
            return

        new_name = new_name.strip()

        # Get currently selected item
        dest_tree = self.query_one("#dest_tree", Tree)
        if not dest_tree.cursor_node or dest_tree.cursor_node == dest_tree.root:
            self.notify("⚠️ No item selected", severity="warning")
            return

        node_id = str(id(dest_tree.cursor_node))
        if node_id not in self.node_to_path:
            self.notify("⚠️ Cannot rename this item", severity="warning")
            return

        old_path = self.node_to_path[node_id]

        # Calculate new path
        if old_path.parent != Path("."):
            new_path = old_path.parent / new_name
        else:
            new_path = Path(new_name)

        # Check if new name already exists
        if new_path in self.dest_structure and new_path != old_path:
            self.notify(f"⚠️ '{new_name}' already exists", severity="warning")
            return

        # Perform rename: need to update all paths that start with old_path
        items_to_rename = {}
        for dest_path, value in list(self.dest_structure.items()):
            try:
                # Check if this path is the old path or a child of it
                rel = dest_path.relative_to(old_path)
                new_dest_path = new_path / rel if rel != Path(".") else new_path
                items_to_rename[dest_path] = (new_dest_path, value)
            except ValueError:
                # Not a child of old_path
                if dest_path == old_path:
                    items_to_rename[dest_path] = (new_path, value)

        # Remove old paths and add new ones
        for old_p, (new_p, value) in items_to_rename.items():
            del self.dest_structure[old_p]
            self.dest_structure[new_p] = value

            # Update expanded paths
            if old_p in self.expanded_paths:
                self.expanded_paths.discard(old_p)
                self.expanded_paths.add(new_p)

        self._update_dest_tree()
        self.notify(f"✓ Renamed: {old_path.name} → {new_name}")

    def _get_current_dest_folder(self) -> Path:
        """Get the current destination folder based on cursor position in dest tree."""
        dest_tree = self.query_one("#dest_tree", Tree)

        # If nothing selected or root selected, return root
        if not dest_tree.cursor_node or dest_tree.cursor_node == dest_tree.root:
            return Path(".")

        # Get the path for the selected node
        node_id = str(id(dest_tree.cursor_node))
        if node_id not in self.node_to_path:
            return Path(".")

        selected_path = self.node_to_path[node_id]

        # Check if it's a directory in our structure
        if selected_path in self.dest_structure:
            is_dir, _ = self.dest_structure[selected_path]
            if is_dir:
                # It's a directory, use it
                return selected_path
            else:
                # It's a file, use its parent
                return (
                    selected_path.parent
                    if selected_path.parent != Path(".")
                    else Path(".")
                )

        return Path(".")

    def action_remove_selected(self) -> None:
        """Remove selected item from destination."""
        dest_tree = self.query_one("#dest_tree", Tree)
        if not dest_tree.cursor_node or dest_tree.cursor_node == dest_tree.root:
            self.notify("⚠️ No item selected in package", severity="warning")
            return

        # Get the path for this node
        node_id = str(id(dest_tree.cursor_node))
        if node_id not in self.node_to_path:
            self.notify("⚠️ Could not find path for selected item", severity="warning")
            return

        selected_path = self.node_to_path[node_id]

        # Remove this path and all children
        items_to_remove = []
        for dest_path in self.dest_structure.keys():
            # Check if this is the selected path or a child of it
            try:
                dest_path.relative_to(selected_path)
                items_to_remove.append(dest_path)
            except ValueError:
                # Not a child, check if it's the exact match
                if dest_path == selected_path:
                    items_to_remove.append(dest_path)

        if items_to_remove:
            for item in items_to_remove:
                del self.dest_structure[item]
            self._update_dest_tree()
            self.notify(
                f"✓ Removed: {selected_path.name} ({len(items_to_remove)} item(s))"
            )
        else:
            self.notify("⚠️ Could not find item to remove", severity="warning")

    def action_clear_dest(self) -> None:
        """Clear all items from destination."""
        self.dest_structure.clear()
        self._update_dest_tree()

    def _add_to_destination(
        self, source_path: Path, dest_base: Path = Path(".")
    ) -> None:
        """Add a file or directory to the destination structure.

        Args:
            source_path: The source file or directory to add
            dest_base: The destination base folder to add into
        """
        source_path = Path(source_path)

        # Calculate relative path from source_dir
        try:
            rel_path = source_path.relative_to(self.source_dir)
        except ValueError:
            # If not relative to source_dir, just use the name
            rel_path = Path(source_path.name)

        # Combine with destination base
        if dest_base != Path("."):
            final_path = dest_base / rel_path.name
        else:
            final_path = rel_path

        # Check if already exists
        if final_path in self.dest_structure:
            self.notify(f"⚠️ Already exists: {final_path}", severity="warning")
            return

        if source_path.is_file():
            # Add single file
            self.dest_structure[final_path] = (False, source_path)
        elif source_path.is_dir():
            # Add directory and all contents recursively
            self.dest_structure[final_path] = (True, source_path)
            # Mark this directory as expanded so user can see what was added
            self.expanded_paths.add(final_path)

            for item in source_path.rglob("*"):
                item_rel_to_source = item.relative_to(source_path)
                item_final_path = final_path / item_rel_to_source

                if item.is_file():
                    self.dest_structure[item_final_path] = (False, item)
                elif item.is_dir():
                    self.dest_structure[item_final_path] = (True, item)

        # If we added to a non-root folder, make sure it's expanded
        if dest_base != Path("."):
            self.expanded_paths.add(dest_base)

        self._update_dest_tree()
        if dest_base != Path("."):
            self.notify(f"✓ Added to {dest_base}: {rel_path.name}")
        else:
            self.notify(f"✓ Added: {final_path}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "create_zip_btn":
            self._create_archive("zip")
        elif event.button.id == "create_tar_btn":
            self._create_archive("tar.gz")
        elif event.button.id == "clear_btn":
            self.action_clear_dest()
        elif event.button.id == "cancel_btn":
            self.post_message(self.Packaged(None))

    def _create_archive(self, format: str) -> None:
        """Create archive from destination structure."""
        if not self.dest_structure:
            self.notify("⚠️ Package is empty! Add files first.", severity="warning")
            return

        # Get archive name
        name_input = self.query_one("#archive_name_input", Input)
        archive_name = name_input.value.strip()
        if not archive_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"package_{timestamp}"

        # Remove extension if user added it
        archive_name = (
            archive_name.removesuffix(".zip")
            .removesuffix(".tar.gz")
            .removesuffix(".tar")
        )

        # Create temporary directory for staging
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            staging_dir = temp_path / "package"
            staging_dir.mkdir()

            # Copy files to staging directory
            self.notify("📦 Copying files to staging area...")
            for dest_path, (is_dir, source_path) in self.dest_structure.items():
                target = staging_dir / dest_path

                if is_dir:
                    # Create directory (even if it's virtual with no source)
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    # Copy file
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if source_path.exists() and source_path != Path("<virtual>"):
                        shutil.copy2(source_path, target)

            # Create archive in current working directory
            output_dir = Path.cwd()

            if format == "zip":
                archive_path = output_dir / f"{archive_name}.zip"
                self.notify(f"🗜️ Creating ZIP archive: {archive_path}")
                with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in staging_dir.rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(staging_dir)
                            zipf.write(file_path, arcname)
            else:  # tar.gz
                archive_path = output_dir / f"{archive_name}.tar.gz"
                self.notify(f"🗜️ Creating TAR.GZ archive: {archive_path}")
                with tarfile.open(archive_path, "w:gz") as tar:
                    tar.add(staging_dir, arcname=Path(archive_name))

            self.notify(f"✅ Archive created: {archive_path}", severity="information")
            self.post_message(self.Packaged(archive_path))
