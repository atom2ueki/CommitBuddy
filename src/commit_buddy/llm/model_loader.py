"""
Model loading utilities for Commit Buddy.
"""
import os
import sys
import io
from contextlib import redirect_stderr, redirect_stdout
from typing import Optional

from langchain_community.llms.llamacpp import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from commit_buddy.config import CommitBuddyConfig, load_config

def load_llm(config: Optional[CommitBuddyConfig] = None) -> LlamaCpp:
    """
    Load a LlamaCpp model for use with LangChain.

    Args:
        config: CommitBuddyConfig object. If None, loads default config.

    Returns:
        LlamaCpp: Loaded model.
    """
    if config is None:
        config = load_config()

    # Make sure the model exists
    # Ensure path is properly expanded
    model_path = os.path.expanduser(config.model_path)
    print(f"Looking for model at: {model_path}")

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found at {config.model_path}. "
            f"Please download a model and place it at this location, "
            f"or update your configuration to point to the correct location."
        )

    # Create callback manager for streaming output
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    # Suppress stderr and stdout during model loading to avoid the initialization warnings
    stderr_capture = io.StringIO()
    stdout_capture = io.StringIO()

    try:
        with redirect_stderr(stderr_capture), redirect_stdout(stdout_capture):
            # Load the model
            llm = LlamaCpp(
                model_path=os.path.expanduser(config.model_path),
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                n_ctx=config.context_length,
                n_gpu_layers=config.n_gpu_layers,
                n_batch=config.n_batch,
                callback_manager=callback_manager,
                verbose=config.chain_verbose,
                n_threads=config.n_threads,
            )
    except Exception as e:
        # Re-raise any exceptions
        print(f"Error loading model: {str(e)}")
        raise

    return llm
