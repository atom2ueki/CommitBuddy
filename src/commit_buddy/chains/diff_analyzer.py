"""
LangChain chain for analyzing git diffs.
"""
from typing import Dict, Any, Optional

from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.schema.runnable import RunnableSequence
from langchain.schema.output_parser import StrOutputParser

from commit_buddy.llm.prompts import DIFF_ANALYSIS_PROMPT
from commit_buddy.llm.model_loader import load_llm

def create_diff_analyzer_chain(llm: Optional[BaseLLM] = None) -> RunnableSequence:
    """
    Create a LangChain chain for analyzing git diffs.

    Args:
        llm: LLM to use for the chain. If None, loads a default LLM.

    Returns:
        RunnableSequence: A chain that takes a diff and returns an analysis.
    """
    if llm is None:
        llm = load_llm()

    # Create the chain
    chain = (
        {"diff": lambda x: x["diff"]}
        | DIFF_ANALYSIS_PROMPT
        | llm
        | StrOutputParser()
    )

    return chain

def analyze_diff(diff: str, llm: Optional[BaseLLM] = None) -> str:
    """
    Analyze a git diff to understand what changes were made.

    Args:
        diff: Git diff output.
        llm: LLM to use for the analysis. If None, loads a default LLM.

    Returns:
        str: Analysis of the diff.
    """
    chain = create_diff_analyzer_chain(llm)
    return chain.invoke({"diff": diff})
