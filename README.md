# CommitBuddy

> 🚀 AI-Powered Git Commit Assistant with 🦜️🔗 LangChain

[![PyPI version](https://badge.fury.io/py/commit-buddy.svg)](https://badge.fury.io/py/commit-buddy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CommitBuddy is an AI-powered assistant that analyzes your code changes and generates meaningful commit messages following conventional commit standards. It analyzes git diffs, breaks changes into logical units, and creates semantic commit messages that clearly describe what changed and why.

## Features

- 🔍 **Intelligent Analysis**: Analyzes git diffs to understand code changes
- 🧩 **Logical Grouping**: Splits changes into logical units for atomic commits
- 💬 **Semantic Messages**: Generates commit messages in conventional format
- 🔄 **Multi-Stage Workflow**: Option for full analysis or quick generation
- 🚀 **GPU Acceleration**: Support for Metal (Apple Silicon) and CUDA (NVIDIA)

## Installation

### Basic Installation (CPU)

```bash
pip install commit-buddy
```

### With GPU Acceleration

For Apple Silicon (Metal):
```bash
pip install "commit-buddy[metal]"
```

For NVIDIA GPUs (CUDA):
```bash
pip install "commit-buddy[cuda]"
```

## Setup

1. Download an LLM model file (GGUF format) for local inference
2. Place it in `~/.commitbuddy/models/`
3. Run with `commitbuddy --show-config` to check your configuration

## Usage

### Basic Usage

```bash
# For already staged changes (git add)
commitbuddy

# For unstaged changes
commitbuddy --unstaged
```

### Command Line Options

```
usage: commitbuddy [-h] [--config CONFIG] [--model MODEL] [--analyze] [--unstaged] [--auto-commit] [--verbose] [--show-config] [--gpu-layers GPU_LAYERS]

AI-Powered Git Commit Assistant with LangChain

options:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Path to config file
  --model MODEL, -m MODEL
                        Path to LLM model file
  --analyze, -a         Analyze git diff without making any commits
  --unstaged, -u        Include unstaged changes in the analysis
  --auto-commit, -ac    Automatically commit changes without confirmation
  --verbose, -v         Enable verbose output
  --show-config         Show configuration and exit
  --gpu-layers GPU_LAYERS, -g GPU_LAYERS
                        Number of layers to run on GPU (for Metal/CUDA acceleration)
```

## Configuration

CommitBuddy creates a default configuration file at `~/.commitbuddy/config.yaml`. You can customize this file to change settings:

```yaml
# LLM settings
model_path: ~/.commitbuddy/models/your-model.gguf
context_length: 4096
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
commit_scopes: []
```

## Recommended Models

CommitBuddy works best with coding-specialized language models. Here are some recommended options:

- [Qwen2.5-7B-Coder-GGUF](https://huggingface.co/Qwen/Qwen2.5-7B-Coder-GGUF)
- [CodeLlama-7B-Instruct-GGUF](https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF)
- [WizardCoder-Python-13B-GGUF](https://huggingface.co/TheBloke/WizardCoder-Python-13B-V1.0-GGUF)

Download the quantized model (Q4_K_M recommended for good balance of speed/quality) and place it in your `~/.commitbuddy/models/` directory.

## Examples

### Analyzing Staged Changes

```bash
$ git add src/core/utils.py src/api/routes.py
$ commitbuddy
```

![Example Output](./assets/example-output.png)

### Analyzing Unstaged Changes

```bash
$ commitbuddy --unstaged
```

### Analyzing Without Committing

```bash
$ commitbuddy --analyze
```

## How It Works

CommitBuddy uses a multi-stage LangChain pipeline:

1. **Diff Analysis**: Analyzes git diffs to understand what changed
2. **Change Splitting**: Groups related files into logical units
3. **Message Generation**: Creates conventional commit messages

Each stage feeds into the next, creating a comprehensive analysis that results in meaningful commit messages.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the LLM integration
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) for local inference
- [Rich](https://github.com/Textualize/rich) for terminal formatting
- [GitPython](https://github.com/gitpython-developers/GitPython) for git operations
