# CommitBuddy 🤖

🚀 An AI-powered Git commit assistant that uses LangChain and local LLMs to analyze your code changes, split them into logical units, and generate semantic commit messages 🚀

[![Release](https://github.com/atom2ueki/CommitBuddy/actions/workflows/release.yml/badge.svg)](https://github.com/atom2ueki/CommitBuddy/actions/workflows/release.yml)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

## Features

- Analyzes git diffs to understand code changes
- Splits changes into logical units for atomic commits
- Generates conventional commit messages
- Works with local LLM models via llama-cpp-python
- Uses LangChain for sophisticated LLM prompting and chaining
- Fully configurable via yaml file

## Architecture

Commit Buddy integrates several key technologies:

1. **LangChain:** Used to create sophisticated prompts and process chains for analyzing diffs, splitting changes, and generating commit messages
2. **llama-cpp-python:** Powers the local LLM inference for understanding code changes
3. **GitPython:** Handles all Git operations
4. **Rich:** Provides beautiful terminal output

## Installation

### Prerequisites

- Python 3.9 or higher
- Git
- A compatible LLM model (e.g., Llama, Mistral, etc.)

### From PyPI

```bash
pip install commit-buddy
```

### From Source

```bash
git clone https://github.com/atom2ueki/commitbuddy.git
cd commitbuddy
pip install -e .
```

### Optional Accelerated Backends

You can install Commit Buddy with hardware acceleration:

```bash
# For Apple Silicon (Metal)
pip install "commit-buddy[metal]" --extra-index-url https://download.pytorch.org/whl/nightly/cpu

# For NVIDIA GPUs (CUDA)
pip install "commit-buddy[cuda]" --extra-index-url https://download.pytorch.org/whl/cu118
```

## Configuration

Commit Buddy uses a configuration file located at `~/.commitbuddy/config.yml`. A default configuration is created the first time you run the tool.

You can specify a custom configuration file with the `--config` command-line option.

Example configuration:

```yaml
# LLM settings
model_path: ~/.commitbuddy/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
context_length: 8192
temperature: 0.2
max_tokens: 1024
n_gpu_layers: 1
n_batch: 512
n_threads: 4

# Git settings
git_command: git
auto_commit: false

# LangChain settings
chain_verbose: false

# Commit message settings
commit_types:
  - feat
  - fix
  - docs
  - style
  - refactor
  - perf
  - test
  - build
  - ci
  - chore
  - revert

commit_scopes:
  - ui
  - api
  - db
  - auth
```

## Usage

### Basic Usage

```bash
# Analyze staged changes and commit them
commitbuddy

# Include unstaged changes
commitbuddy --unstaged

# Only analyze changes without committing
commitbuddy --analyze

# Automatically commit without confirmation
commitbuddy --auto-commit
```

### Command Line Options

- `--config`, `-c`: Path to config file
- `--model`, `-m`: Path to LLM model file
- `--analyze`, `-a`: Analyze git diff without making any commits
- `--unstaged`, `-u`: Include unstaged changes in the analysis
- `--auto-commit`, `-ac`: Automatically commit changes without confirmation
- `--verbose`, `-v`: Enable verbose output

## How It Works

1. **Diff Analysis**: Commit Buddy analyzes your git diff to understand the changes.
2. **Change Splitting**: It splits the changes into logical units that should be committed separately.
3. **Commit Message Generation**: For each logical unit, it generates a semantic commit message.
4. **Commit**: After confirmation, it commits each logical unit with its generated message.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
