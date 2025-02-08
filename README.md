# CommitBuddy - Your AI-Powered Git Commit Assistant

CommitBuddy is a command-line tool that generates semantic commit messages using an AI assistant powered by the Ollama CLI. With a fun, interactive, and step-by-step process, CommitBuddy helps you craft clear, conventional commit messages while adding a bit of humor to your Git workflow.

## Features

- **Step-by-Step Process:**  
  Follow along as CommitBuddy loads your configuration, retrieves staged changes, generates an AI-powered commit message, and (optionally) commits the changes—all with fun emojis and informative messages.

- **Interactive Options:**  
  After generating a commit message, choose from:
  - **Y**: Accept & commit the changes.
  - **R**: Regenerate a new commit message.
  - **N**: Abort the commit process.

- **Diagnostic Check:**  
  The `doctor` command verifies your configuration, confirms that the Ollama CLI is installed, and tests connectivity to your Ollama server.

## Requirements

- Python 3.6 or higher
- [Git](https://git-scm.com/) (your project must be under Git version control)
- [Ollama CLI](https://ollama.ai/) installed and configured

## Setup

It is **highly recommended** to use a virtual environment to manage dependencies when building and using CommitBuddy.

If you just want to try it out without install cli tool, just making the main.py executable first

```bash
chmod +x main.py 
```

### 1. Create a Virtual Environment

Open your terminal in the project root and run:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

### 2. Install Dependencies

CommitBuddy uses only Python's standard library, but we include a `requirements.txt` file (for example, to ensure you have the correct version of `setuptools`). To install all necessary dependencies, run:

```bash
pip install -r requirements.txt
```

### 3. Install CommitBuddy

Clone or download the repository, then install it in editable mode:

```bash
pip install --editable .
```

This command creates the `commitbuddy` command-line entry point in your virtual environment.

### 4. Configure CommitBuddy

Create a `config.json` file in the project root with your Ollama settings. For example:

```json
{
  "model": "your-model-name",
  "ollamaIp": "127.0.0.1"
}
```

> **Note:** Replace `"your-model-name"` with the identifier of the model you want to use (e.g., `"gpt-4"`) and adjust `"127.0.0.1"` if your Ollama server is hosted at a different address.

## Usage

After installation and configuration, you can use CommitBuddy via the following commands:

### Generate a Commit Message

This command generates a semantic commit message from your staged Git changes, displays the message, and offers you three options (accept, regenerate, or abort):

```bash
commitbuddy generate
```

When you run this command, you'll see progress messages like:

- **Step 1/5:** Loading configuration (🔍)
- **Step 2/5:** Retrieving staged changes (📄)
- **Step 3/5:** Generating commit message with AI assistance (🤖)
- **Step 5/5:** Committing changes (🚀)

After the commit message is generated, you'll be prompted:

```
What do you want to do next? Choose an option:
👉 [Y] Accept & commit
👉 [R] Regenerate commit message
👉 [N] Abort
Your choice (Y/R/N):
```

### Run Diagnostic Check

The `doctor` command runs a diagnostic check to ensure that your configuration is correct, the Ollama CLI is installed, and connectivity to your Ollama server is working:

```bash
commitbuddy doctor
```

## Packaging and Distribution

If you wish to distribute CommitBuddy, you can build a source distribution using:

```bash
python setup.py sdist bdist_wheel
```

Then, you can upload it to PyPI or share it directly with others.

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please open issues or submit pull requests if you have suggestions or improvements.

---

Enjoy your interactive, AI-powered commit message generator—**CommitBuddy**! 🚀😄