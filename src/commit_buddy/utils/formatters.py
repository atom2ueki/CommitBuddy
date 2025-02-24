"""
Output formatting utilities for Commit Buddy.
"""
from typing import List, Dict, Any
import os
import re

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text
from rich.columns import Columns
from rich.tree import Tree

from commit_buddy.chains.change_splitter import LogicalChangeUnit

console = Console()

def format_diff_analysis(analysis: str) -> None:
    """
    Format and print a diff analysis.

    Args:
        analysis: Diff analysis text.
    """
    console.print(Panel(
        Markdown(analysis),
        title="Diff Analysis",
        border_style="blue"
    ))

def format_logical_units(units: List[LogicalChangeUnit]) -> None:
    """
    Format and print a list of logical change units.

    Args:
        units: List of LogicalChangeUnit objects.
    """
    table = Table(title="Logical Change Units")

    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Files", style="cyan")
    table.add_column("Explanation")
    table.add_column("Split?", style="green")

    for i, unit in enumerate(units):
        table.add_row(
            str(i + 1),
            unit.name,
            ", ".join(unit.files),
            unit.explanation[:100] + ("..." if len(unit.explanation) > 100 else ""),
            "✓" if unit.should_split else "✗"
        )

    console.print(table)

    # Also display a tree view for better visualization
    if len(units) > 1:
        tree = Tree("📁 Logical Units")

        for i, unit in enumerate(units):
            branch = tree.add(f"[bold]{unit.name}[/bold]")
            for file in unit.files:
                branch.add(f"[cyan]{file}[/cyan]")

        console.print(tree)

def format_commit_message(message: str) -> None:
    """
    Format and print a commit message.

    Args:
        message: Commit message.
    """
    if not message or message.isspace():
        console.print(Panel(
            "[red]Empty commit message generated[/red]",
            title="Commit Message",
            border_style="red"
        ))
        return

    # Split the message for better formatting
    lines = message.split("\n")

    if lines:
        # Format the first line (subject) differently
        subject = lines[0].strip()

        # Find commit type and scope if present
        match = re.match(r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9_-]+\))?:', subject, re.IGNORECASE)

        if match:
            type_part = match.group(1)
            scope_part = match.group(2) or ""
            # Extract the description (everything after the colon)
            colon_index = subject.find(':')
            if colon_index != -1 and colon_index + 1 < len(subject):
                desc_part = subject[colon_index + 1:].strip()
            else:
                desc_part = ""

            # Create rich text with different colors
            text = Text()
            text.append(type_part, style="bold green")
            if scope_part:
                text.append(scope_part, style="blue")
            text.append(":", style="white")
            text.append(" " + desc_part, style="yellow")

            # Create a panel for the subject line
            subject_panel = Panel(
                text,
                title="Subject",
                border_style="green"
            )

            console.print(subject_panel)

            # Format the body if present
            if len(lines) > 1:
                body = "\n".join(lines[1:]).strip()
                if body:
                    body_panel = Panel(
                        Markdown(body),
                        title="Body",
                        border_style="blue"
                    )
                    console.print(body_panel)

            return

        # If we get here, the format wasn't recognized as conventional commit format
        # Just display the raw message
        console.print(Panel(
            Markdown(f"```\n{message}\n```"),
            title="Commit Message",
            border_style="yellow",
            subtitle="Note: Not in conventional commit format"
        ))
    else:
        # Empty message
        console.print(Panel(
            "No commit message generated",
            title="Commit Message",
            border_style="red"
        ))

def format_error(error: str) -> None:
    """
    Format and print an error message.

    Args:
        error: Error message.
    """
    console.print(Panel(
        error,
        title="Error",
        border_style="red"
    ))

def format_success(message: str) -> None:
    """
    Format and print a success message.

    Args:
        message: Success message.
    """
    console.print(Panel(
        message,
        title="Success",
        border_style="green"
    ))

def format_file_diff(file_path: str, diff: str) -> None:
    """
    Format and print a file diff.

    Args:
        file_path: Path to the file.
        diff: Diff content.
    """
    console.print(f"[bold]File:[/bold] {file_path}")
    console.print(Syntax(diff, "diff", theme="monokai"))

def format_file_changes_summary(files: List[str], changes: Dict[str, List[str]]) -> None:
    """
    Format and print a summary of file changes.

    Args:
        files: List of file names
        changes: Dictionary of changes per file
    """
    file_trees = []

    for file in files:
        tree = Tree(f"[bold cyan]{file}[/bold cyan]")

        if file in changes and changes[file]:
            for i, change in enumerate(changes[file][:5]):
                if len(change) > 60:
                    change = change[:57] + "..."
                tree.add(f"[green]+ {change}[/green]")

            if len(changes[file]) > 5:
                tree.add(f"[dim]... and {len(changes[file]) - 5} more changes[/dim]")
        else:
            tree.add("[dim]No content changes detected[/dim]")

        file_trees.append(tree)

    # If many files, just show counts
    if len(files) > 10:
        console.print(f"[bold]Files changed:[/bold] {len(files)}")
        # Group by extension
        extensions = {}
        for file in files:
            ext = os.path.splitext(file)[1] or "(no extension)"
            if ext not in extensions:
                extensions[ext] = 0
            extensions[ext] += 1

        ext_table = Table(title="Files by Type")
        ext_table.add_column("Extension", style="cyan")
        ext_table.add_column("Count", style="green")

        for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
            ext_table.add_row(ext, str(count))

        console.print(ext_table)

        # Just show first few files
        for tree in file_trees[:5]:
            console.print(tree)
        console.print(f"[dim]... and {len(files) - 5} more files[/dim]")
    else:
        # Show all files in a column layout
        console.print(Columns(file_trees))
