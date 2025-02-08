#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
import requests

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    print("🔍 [Step 1/5] Loading configuration from config.json...")
    if not os.path.exists(config_path):
        print("❌ Configuration file not found! Please create a config.json file in the project root.")
        sys.exit(1)
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        if 'model' not in config or 'ollamaIp' not in config:
            print("❌ config.json is missing required keys ('model' and/or 'ollamaIp').")
            sys.exit(1)
        print("✅ Configuration loaded successfully!")
        return config
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        sys.exit(1)

def get_staged_diff():
    print("📄 [Step 2/5] Retrieving staged diff from Git...")
    try:
        diff = subprocess.check_output(
            ["git", "diff", "--cached"],
            stderr=subprocess.STDOUT,
            text=True
        )
        if not diff.strip():
            print("⚠️ No staged changes found! Please stage your changes and try again.")
            sys.exit(1)
        print("✅ Staged diff retrieved!")
        return diff
    except subprocess.CalledProcessError as e:
        print(f"❌ Error retrieving git diff: {e.output}")
        sys.exit(1)

def generate_commit_message_http(diff, config):
    print("🤖 [Step 3/5] Generating commit message via HTTP...")
    url = f"http://{config['ollamaIp']}/api/generate"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""
You are an assistant that writes commit messages following the Conventional Commits specification.
Based on the following diff of staged changes, generate a clear, concise commit message.
Be sure to use one of the following prefixes as appropriate: "feat:", "fix:", "docs:", "style:", "refactor:", "test:", or "chore:".
IMPORTANT: Respond ONLY with the commit message text, without any markdown formatting, code blocks, or backticks.
The message should be a single line without any wrapping or additional formatting.

Diff:
{diff}

Commit message:
""".strip()
    
    payload = {
        "model": config["model"],
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        # Parse the JSON response
        result = response.json()
        # Extract just the response field and clean it up
        commit_message = result.get('response', '').strip()
        # Remove markdown code blocks if present
        commit_message = commit_message.strip('`')
        # Remove any 'markdown' or other language specifiers that might appear
        if '\n' in commit_message:
            commit_message = commit_message.split('\n', 1)[1]
        commit_message = commit_message.strip()
        if not commit_message:
            raise ValueError("Empty response from Ollama")
        print("✅ Commit message generated!")
        return commit_message
    except requests.RequestException as e:
        print("❌ Error generating commit message via HTTP:")
        print(e)
        sys.exit(1)
    except (ValueError, KeyError) as e:
        print("❌ Error processing Ollama response:")
        print(e)
        sys.exit(1)

def prompt_user(question):
    return input(question)

def commit_changes(commit_message):
    print("🚀 [Step 5/5] Committing changes with Git...")
    try:
        subprocess.check_call(["git", "commit", "-m", commit_message])
        print("🎉 Changes committed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error committing changes: {e}")
        sys.exit(1)

def generate_command():
    config = load_config()
    diff = get_staged_diff()
    
    while True:
        commit_message = generate_commit_message_http(diff, config)
        print("\n📣 Here is the generated commit message:")
        print("---------------------------------------------------")
        print(commit_message)
        print("---------------------------------------------------\n")
        print("What do you want to do next? Choose an option:")
        print("👉 [Y] Accept & commit")
        print("👉 [R] Regenerate commit message")
        print("👉 [N] Abort")
        
        choice = prompt_user("Your choice (Y/R/N): ").strip().lower()
        if choice == 'y':
            commit_changes(commit_message)
            break
        elif choice == 'r':
            print("🔄 Regenerating commit message... Hang tight! 😎")
            continue  # Re-loop to regenerate
        elif choice == 'n':
            print("🚫 Aborting commit. No changes were committed.")
            break
        else:
            print("❓ Invalid option! Please enter Y, R, or N.")

def doctor_command():
    print("🩺 Running doctor check for CommitBuddy (HTTP mode)...")
    config = load_config()
    print("🌐 Checking connectivity to Ollama server via HTTP...")
    try:
        url = f"http://{config['ollamaIp']}/api/tags"
        response = requests.get(url)
        response.raise_for_status()
        print("✅ Connected to Ollama server successfully! Here's some info:")
        print(json.dumps(response.json(), indent=2))
    except requests.RequestException as e:
        print("❌ Error connecting to Ollama server. Details:")
        print(e)
        sys.exit(1)
    print("🩺 Doctor check completed. Everything looks good!")

def main():
    parser = argparse.ArgumentParser(
        description="CommitBuddy - Your AI-Powered Git Commit Assistant (HTTP mode)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("generate", help="Generate commit message and optionally commit changes")
    subparsers.add_parser("doctor", help="Run a diagnostic check on the tool and Ollama connectivity")
    
    args = parser.parse_args()
    if args.command == "generate":
        generate_command()
    elif args.command == "doctor":
        doctor_command()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()