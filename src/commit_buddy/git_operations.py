"""
Git operations using GitPython.
"""
import os
import subprocess
from typing import List, Dict, Any, Optional, Tuple

import git
from git import Repo, GitCommandError

from commit_buddy.chains.change_splitter import LogicalChangeUnit

def get_repo(path: Optional[str] = None) -> Repo:
    """
    Get a GitPython Repo object for the current repository.

    Args:
        path: Path to the git repository. If None, uses current directory.

    Returns:
        git.Repo: GitPython Repo object.

    Raises:
        git.exc.InvalidGitRepositoryError: If the directory is not a git repository.
    """
    if path is None:
        path = os.getcwd()

    return Repo(path)

def get_diff(repo: Optional[Repo] = None, staged: bool = True) -> str:
    """
    Get the git diff output.

    Args:
        repo: GitPython Repo object. If None, gets the repo from the current directory.
        staged: Whether to get diff for staged changes or all changes.

    Returns:
        str: Git diff output.
    """
    if repo is None:
        repo = get_repo()

    if staged:
        return repo.git.diff("--staged")
    else:
        return repo.git.diff()

def stage_files(repo: Optional[Repo] = None, files: List[str] = None) -> None:
    """
    Stage specific files or parts for commit.

    Args:
        repo: GitPython Repo object. If None, gets the repo from the current directory.
        files: List of files to stage. If None, stages all changes.
    """
    if repo is None:
        repo = get_repo()

    if files is None:
        repo.git.add("--all")
    else:
        for file in files:
            repo.git.add(file)

def commit_changes(repo: Optional[Repo] = None, message: str = "commit") -> None:
    """
    Commit staged changes.

    Args:
        repo: GitPython Repo object. If None, gets the repo from the current directory.
        message: Commit message.
    """
    if repo is None:
        repo = get_repo()

    # Ensure the message is properly formatted for git
    # Remove any triple backticks, newlines at beginning or end
    cleaned_message = message.replace("```", "").strip()

    # Commit the changes
    repo.git.commit("-m", cleaned_message)

def commit_logical_unit(
    unit: LogicalChangeUnit,
    commit_message: str,
    repo: Optional[Repo] = None
) -> bool:
    """
    Commit a logical unit of changes.

    Args:
        unit: LogicalChangeUnit object describing the changes.
        commit_message: Commit message.
        repo: GitPython Repo object. If None, gets the repo from the current directory.

    Returns:
        bool: True if the commit was successful, False otherwise.
    """
    if repo is None:
        repo = get_repo()

    try:
        # Reset the staging area
        repo.git.reset()

        # Stage only the files relevant to this logical unit
        for file in unit.files:
            try:
                repo.git.add(file)
            except GitCommandError as e:
                print(f"Warning: Could not add file {file}: {e}")

        # Commit the changes
        commit_changes(repo, commit_message)

        return True
    except (GitCommandError, Exception) as e:
        print(f"Error committing logical unit: {e}")
        return False
