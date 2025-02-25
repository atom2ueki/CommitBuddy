"""
LangChain chain for generating semantic commit messages.
"""
from typing import Dict, Any, List, Optional
import re
import os

from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.schema.runnable import RunnableSequence
from langchain.schema.output_parser import StrOutputParser
from rich.console import Console

from commit_buddy.llm.prompts import COMMIT_MESSAGE_PROMPT
from commit_buddy.llm.model_loader import load_llm
from commit_buddy.config import CommitBuddyConfig, load_config

console = Console()

def create_message_generator_chain(
    llm: Optional[BaseLLM] = None,
    config: Optional[CommitBuddyConfig] = None
) -> RunnableSequence:
    """
    Create a LangChain chain for generating semantic commit messages.

    Args:
        llm: LLM to use for the chain. If None, loads a default LLM.
        config: Configuration object. If None, loads default config.

    Returns:
        RunnableSequence: A chain that takes a change description and returns a commit message.
    """
    if llm is None:
        llm = load_llm()

    if config is None:
        config = load_config()

    # Create the chain
    chain = (
        {
            "change_description": lambda x: x["change_description"],
            "commit_types": lambda x: ", ".join(config.commit_types),
            "commit_scopes": lambda x: ", ".join(config.commit_scopes) if config.commit_scopes else "None specified"
        }
        | COMMIT_MESSAGE_PROMPT
        | llm
        | StrOutputParser()
    )

    return chain

def is_conventional_commit_format(message: str) -> bool:
    """
    Check if a message follows the conventional commit format.

    Args:
        message: Message to check

    Returns:
        bool: True if the message follows the conventional format
    """
    # Match pattern: type(optional_scope): description
    pattern = r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9_-]+\))?:\s+.+'
    return bool(re.match(pattern, message, re.IGNORECASE))

def extract_changed_files(change_description: str) -> List[str]:
    """
    Extract list of changed files from change description.

    Args:
        change_description: Description of changes

    Returns:
        List[str]: List of changed files
    """
    files = []

    # Look for "Files changed:" or similar patterns
    for line in change_description.split('\n'):
        if "Files changed:" in line or "Files:" in line:
            parts = re.split(r'Files changed:|Files:', line, 1)
            if len(parts) > 1:
                file_list = parts[1].strip()
                files = [f.strip() for f in file_list.split(',')]
                break

    return files

def generate_commit_message(
    change_description: str,
    llm: Optional[BaseLLM] = None,
    config: Optional[CommitBuddyConfig] = None
) -> str:
    """
    Generate a semantic commit message for a change.

    Args:
        change_description: Description of the changes.
        llm: LLM to use for the generation. If None, loads a default LLM.
        config: Configuration object. If None, loads default config.

    Returns:
        str: Generated commit message.
    """
    # Extract changed files for potential fallback
    files = extract_changed_files(change_description)

    try:
        # Create the chain and get response
        chain = create_message_generator_chain(llm, config)
        response = chain.invoke({"change_description": change_description})

        # For debugging
        # console.print(f"[dim]Raw response:[/dim]\n{response}")

        # Clean up the message
        message = clean_commit_message(response)

        # Validate message format
        if not is_conventional_commit_format(message):
            # Try to fix common issues
            fixed_message = fix_commit_format(message, files)
            if is_conventional_commit_format(fixed_message):
                return fixed_message

            # If still not valid, create a fallback message
            return generate_fallback_message(files)

        return message

    except Exception as e:
        console.print(f"[red]Error generating commit message: {str(e)}[/red]")
        return generate_fallback_message(files)

def fix_commit_format(message: str, files: List[str]) -> str:
    """
    Attempt to fix common issues with commit message format.

    Args:
        message: Commit message to fix
        files: List of changed files

    Returns:
        str: Fixed commit message
    """
    commit_types = ["feat", "fix", "docs", "style", "refactor",
                  "perf", "test", "build", "ci", "chore", "revert"]

    # Remove separators that might have been copied from the prompt
    message = re.sub(r'-{3,}', '', message)

    # Check for messages without a type prefix
    if not any(message.lower().startswith(t) for t in commit_types):
        # If it contains a colon anywhere, it might be malformed
        if ':' in message:
            parts = message.split(':', 1)

            # Check if the part before colon contains any of the valid types
            before_colon = parts[0].lower()
            for t in commit_types:
                if t in before_colon:
                    # Extract the type and add it properly
                    return f"{t}: {parts[1].strip()}"

            # No valid type found, use a default type
            if len(parts) > 1 and parts[1].strip():
                return f"chore: {parts[1].strip()}"

        # No colon, just add a prefix
        file_type = get_file_type_prefix(files)
        return f"{file_type}: {message.strip()}"

    # Message starts with type but might be malformed
    for t in commit_types:
        if message.lower().startswith(t) and not message.lower().startswith(f"{t}:"):
            # Find where the type ends and add a colon if needed
            parts = re.split(r'[\s\(\)]', message[len(t):].strip(), 1)
            if parts and parts[0]:
                # Might have a scope
                if parts[0].startswith('(') and ')' in message:
                    scope_end = message.find(')', len(t))
                    if scope_end > 0:
                        return f"{t}{message[len(t):scope_end+1]}: {message[scope_end+1:].strip()}"

            # No scope, just add colon
            return f"{t}: {message[len(t):].strip()}"

    # If all else fails, return original
    return message

def get_file_type_prefix(files: List[str]) -> str:
    """
    Determine an appropriate commit type based on file extensions.

    Args:
        files: List of changed files

    Returns:
        str: Appropriate commit type
    """
    if not files:
        return "chore"

    extensions = [os.path.splitext(f)[1].lower() for f in files if os.path.splitext(f)[1]]

    # Count extension occurrences
    ext_count = {}
    for ext in extensions:
        if ext not in ext_count:
            ext_count[ext] = 0
        ext_count[ext] += 1

    # Get most common extension
    most_common = None
    if ext_count:
        most_common = max(ext_count.items(), key=lambda x: x[1])[0]

    # Map extensions to commit types
    if most_common == '.py' or most_common == '.js' or most_common == '.ts':
        return "feat"
    elif most_common == '.md' or most_common == '.txt':
        return "docs"
    elif most_common == '.css' or most_common == '.scss':
        return "style"
    elif most_common == '.test.js' or most_common == '.test.py' or most_common == '.spec.js':
        return "test"
    else:
        return "chore"

def generate_fallback_message(files: List[str]) -> str:
    """
    Generate a fallback commit message based on changed files.

    Args:
        files: List of changed files

    Returns:
        str: Fallback commit message
    """
    if not files:
        return "chore: update repository files"

    # Get prefix based on file types
    prefix = get_file_type_prefix(files)

    # Generate message based on files
    if len(files) == 1:
        filename = os.path.basename(files[0])
        return f"{prefix}: update {filename}"
    elif len(files) <= 3:
        filenames = [os.path.basename(f) for f in files]
        return f"{prefix}: update {', '.join(filenames)}"
    else:
        # Group by file extension
        extensions = {}
        for file in files:
            ext = os.path.splitext(file)[1]
            if not ext:
                ext = "(no extension)"
            if ext not in extensions:
                extensions[ext] = []
            extensions[ext].append(file)

        if len(extensions) == 1:
            ext = list(extensions.keys())[0]
            ext_name = ext[1:] if ext.startswith('.') else ext
            return f"{prefix}: update {len(files)} {ext_name} files"
        else:
            return f"{prefix}: update files across multiple components"

def clean_commit_message(message: str) -> str:
    """
    Clean a commit message by removing markdown formatting and unnecessary whitespace.

    Args:
        message: Raw commit message from LLM.

    Returns:
        str: Cleaned commit message.
    """
    # Remove any triple backticks (code blocks)
    message = message.replace("```", "")

    # Remove any single backticks (inline code)
    message = message.replace("`", "")

    # Remove lines with "IMPORTANT:" and surrounding dashes that might have been copied
    lines = message.split('\n')
    cleaned_lines = []

    skip_line = False
    for line in lines:
        # Skip lines with separators or IMPORTANT
        if re.match(r'-{3,}', line.strip()) or "IMPORTANT:" in line:
            skip_line = True
            continue

        # Skip example header/footer
        if "Example" in line and ("format" in line or "not related" in line):
            skip_line = True
            continue

        # Resume capturing after skipping section
        if skip_line and not line.strip():
            skip_line = False
            continue

        if not skip_line:
            cleaned_lines.append(line)

    # Join remaining lines
    message = '\n'.join(cleaned_lines)

    # Remove any "Now, generate" instructions that might have been copied
    message = re.sub(r'Now,\s+generate.*?changes\s+above\.', '', message, flags=re.IGNORECASE|re.DOTALL)

    # Ensure the message doesn't start with "Commit message:" or similar
    message = re.sub(r'^(Commit message:|\s*message:\s*)', '', message, flags=re.IGNORECASE).strip()

    # Remove text that begins with "Example:" or "Example format:"
    message = re.sub(r'Example(\s+format)?:.*$', '', message, flags=re.IGNORECASE|re.DOTALL).strip()

    # Remove leading/trailing whitespace
    message = message.strip()

    # If message is empty after cleaning, return a fallback
    if not message:
        return "chore: update repository files"

    return message
