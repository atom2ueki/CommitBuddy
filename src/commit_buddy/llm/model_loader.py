# src/commit_buddy/llm/model_loader.py
import os
import sys
import io
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Dict, List, Optional, Union

from langchain_community.llms.llamacpp import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult

from commit_buddy.config import CommitBuddyConfig, load_config

# Define the SilentCallbackHandler directly here to avoid import issues
class SilentCallbackHandler(BaseCallbackHandler):
    """
    Callback handler that captures LLM output but doesn't stream it to stdout.
    """

    def __init__(self):
        super().__init__()
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # Just append to internal buffer without printing
        self.text += token

    # Implement other required methods with just 'pass'
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        pass

    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        pass

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        pass

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        pass

    def on_chain_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        pass

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        pass

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        pass

    def on_tool_end(self, output: str, observation_prefix: Optional[str] = None, **kwargs: Any) -> None:
        pass

    def on_tool_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        pass

    def on_text(self, text: str, **kwargs: Any) -> None:
        pass

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        pass

def load_llm(config: Optional[CommitBuddyConfig] = None, silent: bool = True) -> LlamaCpp:
    """
    Load a LlamaCpp model for use with LangChain.

    Args:
        config: CommitBuddyConfig object. If None, loads default config.
        silent: Whether to suppress token generation output. Default is True.

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

    # Create callback manager based on silent flag
    if silent:
        # Use our custom silent callback handler
        callback_manager = CallbackManager([SilentCallbackHandler()])
    else:
        # Use the standard streaming handler
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
                verbose=False,  # Force verbose to False to avoid extra output
                n_threads=config.n_threads,
            )
    except Exception as e:
        # Re-raise any exceptions
        print(f"Error loading model: {str(e)}")
        raise

    return llm
