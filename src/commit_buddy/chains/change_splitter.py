"""
LangChain chain for splitting git diffs into logical units.
"""
import json
from typing import Dict, Any, List, Optional

from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.schema.runnable import RunnableSequence
from langchain.schema.output_parser import StrOutputParser
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from commit_buddy.llm.prompts import CHANGE_SPLITTING_PROMPT
from commit_buddy.llm.model_loader import load_llm
from commit_buddy.chains.diff_analyzer import analyze_diff

class LogicalChangeUnit(BaseModel):
    """Model for a logical unit of changes."""
    name: str = Field(description="Descriptive name for the logical unit")
    files: List[str] = Field(description="List of files involved in this logical unit")
    explanation: str = Field(description="Brief explanation of what this change accomplishes")
    should_split: bool = Field(description="Whether this logical unit should be split into a separate commit")

class LogicalChangeUnits(BaseModel):
    """Model for a list of logical change units."""
    units: List[LogicalChangeUnit] = Field(description="List of logical change units")

def create_change_splitter_chain(llm: Optional[BaseLLM] = None) -> RunnableSequence:
    """
    Create a LangChain chain for splitting git diffs into logical units.

    Args:
        llm: LLM to use for the chain. If None, loads a default LLM.

    Returns:
        RunnableSequence: A chain that takes a diff and analysis and returns logical units.
    """
    if llm is None:
        llm = load_llm()

    # Create the chain
    chain = (
        {
            "diff": lambda x: x["diff"],
            "analysis": lambda x: x["analysis"]
        }
        | CHANGE_SPLITTING_PROMPT
        | llm
        | StrOutputParser()
    )

    return chain

def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract JSON from text by finding the outermost square brackets.

    Args:
        text: Text that may contain JSON.

    Returns:
        Optional[str]: JSON string if found, None otherwise.
    """
    start_index = text.find('[')

    if start_index == -1:
        return None

    # Find the matching closing bracket
    open_brackets = 0
    for i in range(start_index, len(text)):
        if text[i] == '[':
            open_brackets += 1
        elif text[i] == ']':
            open_brackets -= 1
            if open_brackets == 0:
                return text[start_index:i+1]

    return None

def parse_logical_units(units_str: str) -> List[LogicalChangeUnit]:
    """
    Parse the output of the change splitter chain into a list of LogicalChangeUnit objects.

    Args:
        units_str: JSON string output from the change splitter chain.

    Returns:
        List[LogicalChangeUnit]: List of parsed logical change units.
    """
    # Try to find JSON in the output
    try:
        # Extract JSON using improved method
        json_str = extract_json_from_text(units_str)

        if json_str:
            # Handle potential trailing commas (common LLM error)
            json_str = json_str.replace(',]', ']').replace(',}', '}')
            units_data = json.loads(json_str)

            # Create LogicalChangeUnit objects
            units = [LogicalChangeUnit(**unit) for unit in units_data]

            # Deduplicate by checking for units with the same files and similar explanations
            deduplicated_units = []
            for unit in units:
                is_duplicate = False
                for existing_unit in deduplicated_units:
                    # Check if files match and explanations are similar
                    if set(unit.files) == set(existing_unit.files) and \
                       similar_explanations(unit.explanation, existing_unit.explanation):
                        is_duplicate = True
                        break

                if not is_duplicate:
                    deduplicated_units.append(unit)

            return deduplicated_units
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing logical units: {e}")

        # Fall back to simple file grouping
        print("Falling back to simple file grouping...")
        return create_fallback_units(units_str)

    # Return empty list if parsing fails
    return []

def create_fallback_units(text: str) -> List[LogicalChangeUnit]:
    """
    Create logical units by looking for file patterns in the text.

    Args:
        text: The output from the LLM that failed to parse as JSON.

    Returns:
        List[LogicalChangeUnit]: Simple logical units based on file mentions.
    """
    import re

    # Look for file patterns like *.py, *.js, etc.
    file_pattern = r'[\w\-./]+\.\w+'
    files = re.findall(file_pattern, text)

    if not files:
        return []

    # Group by file extension
    extension_groups = {}
    for file in files:
        ext = file.split('.')[-1]
        if ext not in extension_groups:
            extension_groups[ext] = []
        extension_groups[ext].append(file)

    # Create logical units
    units = []
    for ext, ext_files in extension_groups.items():
        units.append(LogicalChangeUnit(
            name=f"{ext.upper()} Files Update",
            files=ext_files,
            explanation=f"Changes to {ext.upper()} files",
            should_split=True if len(extension_groups) > 1 else False
        ))

    return units

def similar_explanations(explanation1: str, explanation2: str) -> bool:
    """
    Check if two explanations are similar enough to be considered duplicates.

    Args:
        explanation1: First explanation.
        explanation2: Second explanation.

    Returns:
        bool: True if explanations are similar, False otherwise.
    """
    # Simple similarity check based on common words
    words1 = set(explanation1.lower().split())
    words2 = set(explanation2.lower().split())

    # Check what percentage of words are common
    common_words = words1.intersection(words2)

    # If 70% of words are common, consider them similar
    similarity = len(common_words) / max(len(words1), len(words2))
    return similarity > 0.7

def split_changes(diff: str, llm: Optional[BaseLLM] = None) -> List[LogicalChangeUnit]:
    """
    Split a git diff into logical units of changes.

    Args:
        diff: Git diff output.
        llm: LLM to use for the analysis. If None, loads a default LLM.

    Returns:
        List[LogicalChangeUnit]: List of logical change units.
    """
    if llm is None:
        llm = load_llm()

    # First, analyze the diff
    analysis = analyze_diff(diff, llm)

    # Then, split the changes
    chain = create_change_splitter_chain(llm)
    result = chain.invoke({"diff": diff, "analysis": analysis})

    # Parse the result into LogicalChangeUnit objects
    return parse_logical_units(result)
