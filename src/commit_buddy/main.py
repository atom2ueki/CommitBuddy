"""
Main entry point for Commit Buddy with improved logging.
"""
import os
import sys
import argparse
from typing import List, Dict, Any, Optional, Tuple

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

from commit_buddy.config import load_config
from commit_buddy.llm.model_loader import load_llm
from commit_buddy.git_operations import (
    get_repo, get_diff, commit_logical_unit
)
from commit_buddy.chains.diff_analyzer import analyze_diff
from commit_buddy.chains.change_splitter import split_changes, LogicalChangeUnit
from commit_buddy.chains.message_generator import generate_commit_message
from commit_buddy.utils.formatters import (
    format_diff_analysis, format_logical_units,
    format_commit_message, format_error, format_success
)

console = Console()

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="AI-Powered Git Commit Assistant with LangChain"
    )

    parser.add_argument(
        "--config", "-c",
        help="Path to config file"
    )

    parser.add_argument(
        "--model", "-m",
        help="Path to LLM model file"
    )

    parser.add_argument(
        "--analyze", "-a",
        action="store_true",
        help="Analyze git diff without making any commits"
    )

    parser.add_argument(
        "--unstaged", "-u",
        action="store_true",
        help="Include unstaged changes in the analysis"
    )

    parser.add_argument(
        "--auto-commit", "-ac",
        action="store_true",
        help="Automatically commit changes without confirmation"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show configuration and exit"
    )

    parser.add_argument(
        "--gpu-layers", "-g",
        type=int,
        help="Number of layers to run on GPU (for Metal/CUDA acceleration)"
    )

    return parser.parse_args()

def extract_files_from_diff(diff: str) -> List[str]:
    """
    Extract file names from a git diff.

    Args:
        diff: Git diff content

    Returns:
        List[str]: List of file names
    """
    files = []
    for line in diff.split('\n'):
        if line.startswith('diff --git'):
            parts = line.split(' ')
            if len(parts) >= 3:
                file_path = parts[2][2:]  # Remove 'a/' prefix
                files.append(file_path)
    return files

def summarize_changes(diff: str) -> Dict[str, List[str]]:
    """
    Create a simple summary of changes per file.

    Args:
        diff: Git diff content

    Returns:
        Dict[str, List[str]]: Summary of changes per file
    """
    current_file = None
    changes = {}

    for line in diff.split('\n'):
        if line.startswith('diff --git'):
            parts = line.split(' ')
            if len(parts) >= 3:
                current_file = parts[2][2:]  # Remove 'a/' prefix
                changes[current_file] = []
        elif current_file and line.startswith('+') and not line.startswith('+++'):
            # Only track additions for simplicity
            changes[current_file].append(line[1:].strip())

    return changes

def generate_single_commit_message(diff: str, llm, config) -> str:
    """
    Generate a single commit message for all changes without detailed analysis.

    Args:
        diff: Git diff content
        llm: LLM to use for generation
        config: Configuration object

    Returns:
        str: Generated commit message
    """
    files = extract_files_from_diff(diff)

    # Create a simple description
    file_list = ", ".join(files[:10])  # Limit to first 10 files
    if len(files) > 10:
        file_list += f" and {len(files) - 10} more files"

    # Get a summary of changes
    changes_summary = summarize_changes(diff)

    # Create a description that summarizes the changes
    description = f"Changes to the following files: {file_list}\n\n"

    # Add a summary of changes for each file
    for file, changes in changes_summary.items():
        if changes:
            # Limit the number of changes shown
            change_summary = changes[:5]
            if len(changes) > 5:
                change_summary.append(f"... and {len(changes) - 5} more changes")

            description += f"\nFile: {file}\n"
            for change in change_summary:
                if len(change) > 80:
                    change = change[:77] + "..."
                description += f"  + {change}\n"

    # Generate commit message
    return generate_commit_message(description, llm, config)

def handle_logical_unit(
    unit: LogicalChangeUnit,
    llm,
    config,
    auto_commit: bool = False
) -> None:
    """
    Handle a logical change unit, generating a commit message and optionally committing it.

    Args:
        unit: LogicalChangeUnit object.
        llm: LLM to use for generation.
        config: Configuration object.
        auto_commit: Whether to automatically commit without confirmation.
    """
    # Generate a commit message
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Generating commit message for logical unit...[/bold blue]"),
        transient=True,
    ) as progress:
        progress.add_task("generate", total=None)
        change_description = f"# {unit.name}\n\n{unit.explanation}\n\nFiles changed: {', '.join(unit.files)}"
        commit_message = generate_commit_message(change_description, llm, config)

    # Display the commit message
    format_commit_message(commit_message)

    # Ask for confirmation if not auto-commit
    if not auto_commit:
        if not Confirm.ask("Do you want to commit these changes?"):
            return

    # Commit the changes
    try:
        repo = get_repo()
        success = commit_logical_unit(unit, commit_message, repo)

        if success:
            format_success(f"Successfully committed: {commit_message.splitlines()[0]}")
        else:
            format_error("Failed to commit changes.")
    except Exception as e:
        format_error(f"Error committing changes: {e}")

def display_file_changes_summary(diff: str) -> None:
    """
    Display a summary of the file changes.

    Args:
        diff: Git diff content
    """
    files = extract_files_from_diff(diff)

    table = Table(title="Files Changed")
    table.add_column("File", style="cyan")
    table.add_column("Extension", style="green")

    for file in files:
        extension = os.path.splitext(file)[1] or "(no extension)"
        table.add_row(file, extension)

    console.print(table)

def main() -> None:
    """Main entry point for Commit Buddy."""
    args = parse_arguments()

    # Add debugging option
    if args.verbose:
        console.print(f"Running with arguments: {args}")

    try:
        # Load configuration
        config = load_config(args.config)

        # Override config with command line arguments
        if args.model:
            config.model_path = os.path.expanduser(args.model)

        if args.verbose:
            config.chain_verbose = True

        if args.auto_commit:
            config.auto_commit = True

        if args.gpu_layers is not None:
            config.n_gpu_layers = args.gpu_layers
            console.print(f"[blue]Setting GPU layers to {args.gpu_layers}[/blue]")

        # Show configuration and exit if requested
        if args.show_config:
            console.print("[bold]Current Configuration:[/bold]")
            import yaml
            console.print(yaml.dump(config.__dict__))

            # Check if model file exists
            model_path = os.path.expanduser(config.model_path)
            if os.path.exists(model_path):
                console.print(f"[green]Model file exists at: {model_path}[/green]")
                console.print(f"File size: {os.path.getsize(model_path) / (1024*1024):.2f} MB")
            else:
                console.print(f"[red]Model file NOT found at: {model_path}[/red]")

            return

        # Load LLM
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Loading language model...[/bold blue]"),
            transient=True,
        ) as progress:
            progress.add_task("load", total=None)
            llm = load_llm(config)

        # Get git repository
        repo = get_repo()

        # Get diff
        diff = get_diff(repo, not args.unstaged)

        if not diff:
            console.print("[yellow]No changes detected.[/yellow]")
            return

        # Display a summary of file changes
        display_file_changes_summary(diff)

        # If we're analyzing already staged changes (no --unstaged flag),
        # we'll prioritize a simpler workflow
        if not args.unstaged:
            # Quickly generate a commit message without detailed analysis
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Analyzing staged changes and generating commit message...[/bold blue]"),
                transient=True,
            ) as progress:
                progress.add_task("analyze", total=None)
                commit_message = generate_single_commit_message(diff, llm, config)

            format_commit_message(commit_message)

            # Ask for confirmation if not auto-commit
            if not args.auto_commit:
                if not Confirm.ask("Do you want to commit these changes?"):
                    return

            # Commit the changes (all staged files)
            try:
                repo.git.commit("-m", commit_message)
                format_success(f"Successfully committed: {commit_message.splitlines()[0]}")
                return
            except Exception as e:
                format_error(f"Error committing changes: {e}")
                return

        # For unstaged changes or if explicitly analyzing, do the full workflow
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Analyzing changes...[/bold blue]"),
            transient=True,
        ) as progress:
            progress.add_task("analyze", total=None)
            analysis = analyze_diff(diff, llm)

        # Display analysis result
        if args.verbose:
            format_diff_analysis(analysis)
        else:
            # Show a compact summary in non-verbose mode
            analysis_summary = "\n".join(analysis.split("\n")[:5])
            if len(analysis.split("\n")) > 5:
                analysis_summary += "\n..."
            console.print(Panel(analysis_summary, title="Analysis Summary", border_style="blue"))

        # Split changes into logical units
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Splitting changes into logical units...[/bold blue]"),
            transient=True,
        ) as progress:
            progress.add_task("split", total=None)
            logical_units = split_changes(diff, llm)

        if not logical_units:
            console.print("[yellow]No logical units identified. Generating a single commit message instead.[/yellow]")

            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Generating commit message...[/bold blue]"),
                transient=True,
            ) as progress:
                progress.add_task("generate", total=None)
                commit_message = generate_single_commit_message(diff, llm, config)

            format_commit_message(commit_message)

            # Ask for confirmation if not auto-commit
            if not args.auto_commit:
                if not Confirm.ask("Do you want to commit these changes?"):
                    return

            # Commit the changes (all staged files)
            try:
                repo.git.commit("-m", commit_message)
                format_success(f"Successfully committed: {commit_message.splitlines()[0]}")
            except Exception as e:
                format_error(f"Error committing changes: {e}")

            return

        format_logical_units(logical_units)

        # Stop here if only analyzing
        if args.analyze:
            return

        # Process each logical unit
        processed_units = set()  # Track which files we've already committed

        for i, unit in enumerate(logical_units):
            # Skip units that have the same files as ones we've already committed
            unit_files = frozenset(unit.files)
            if unit_files in processed_units:
                console.print(f"[yellow]Skipping unit {i+1}/{len(logical_units)}: {unit.name} (already committed these files)[/yellow]")
                continue

            console.print(f"\n[bold]Processing unit {i+1}/{len(logical_units)}: {unit.name}[/bold]")
            handle_logical_unit(unit, llm, config, args.auto_commit)

            # Track that we've processed these files
            processed_units.add(unit_files)

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        format_error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
