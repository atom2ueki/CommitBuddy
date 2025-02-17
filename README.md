# CommitBuddy 🤖

Your AI-Powered Git Commit Assistant 🚀

[![Release](https://github.com/atom2ueki/CommitBuddy/actions/workflows/release.yml/badge.svg)](https://github.com/atom2ueki/CommitBuddy/actions/workflows/release.yml)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

## 📖 Overview

CommitBuddy is an intelligent command-line tool that revolutionizes your Git workflow by generating semantic commit messages using AI. Powered by the Ollama CLI, it provides a fun, interactive, and step-by-step process to craft clear, conventional commit messages.

## ✨ Key Features

### 🎯 Smart Commit Generation
- AI-powered semantic commit message generation
- Conventional commit format compliance
- Context-aware suggestions based on your changes

### 🔄 Interactive Workflow
- **Step-by-Step Process**: Guided commit creation with progress indicators
- **Multiple Options**:
  - ✅ Accept & commit changes
  - 🔄 Regenerate commit message
  - ❌ Abort process
- **Real-time Feedback**: Clear status updates and error messages

### 🔍 Built-in Diagnostics
- Configuration verification
- Git installation check
- Ollama server connectivity test
- Model availability confirmation

## 🚀 Getting Started

### Prerequisites

- Python 3.6 or higher
- Git (initialized repository)
- [Ollama](https://ollama.ai/) installed and running

### Installation

#### For Users
```bash
pip install commit-buddy
```

#### For Developers
```bash
git clone https://github.com/atom2ueki/commitbuddy
cd commitbuddy
pip install -e .
```

## ⚙️ Configuration

CommitBuddy uses a `.commit-buddy.yml` configuration file with the following search priority:

1. Current project directory
2. Home directory (`~/.commit-buddy.yml`)

### Sample Configuration
```yaml
# Model settings
model: qwen:14b              # Ollama model selection
ollamaIp: localhost:11434    # Ollama server address
```

## 🎮 Usage Guide

### Generate Commit Message
```bash
commitbuddy generate
```

The process follows these steps:
1. 🔍 Loading configuration
2. 📄 Retrieving staged changes
3. 🤖 Generating AI commit message
4. 🎯 Presenting options
5. 🚀 Committing changes (if accepted)

### Interactive Options
```
What would you like to do?
👉 [Y] Accept & commit
👉 [R] Regenerate message
👉 [N] Abort
Your choice (Y/R/N):
```

### Run Diagnostics
```bash
commitbuddy doctor
```

Checks performed:
- ✅ Configuration validation
- ✅ Git installation verification
- ✅ Ollama server connection
- ✅ Model availability

## 🤝 Contributing

We welcome contributions! Whether it's bug fixes, feature additions, or documentation improvements, please feel free to:

1. Fork the repository
2. Create your feature branch
3. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

[Report Bug](https://github.com/atom2ueki/commitbuddy/issues) · [Request Feature](https://github.com/atom2ueki/commitbuddy/issues)
