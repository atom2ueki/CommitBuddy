"""
LangChain prompt templates for Commit Buddy.
"""
from typing import List
from langchain.prompts import PromptTemplate

# Prompt for analyzing git diff and understanding the overall changes
DIFF_ANALYSIS_TEMPLATE = """
You are an expert software engineer tasked with analyzing git diffs to understand code changes.
You're given the output of a git diff command and need to analyze it to understand what changes were made.

Git diff:
```
{diff}
```

Analyze the changes above and provide a CONCISE explanation of what was changed and why.
Focus on understanding the underlying purpose of these changes, not just the surface-level textual changes.

Keep your analysis brief but complete, focusing on:
1. What files were changed
2. A summary of each file's changes
3. The overall purpose of these changes

Analysis:
"""

DIFF_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["diff"],
    template=DIFF_ANALYSIS_TEMPLATE
)

# Prompt for splitting changes into logical units
CHANGE_SPLITTING_TEMPLATE = """
You are an expert software engineer tasked with organizing code changes into logical units for separate commits.
You're given a git diff output, and you need to identify the distinct logical changes that should be committed separately.

Git diff:
```
{diff}
```

Previous analysis:
{analysis}

Split the above changes into separate logical units based on files that should be committed together.
Group files that serve a single purpose or implement a related feature/fix.

RESPOND ONLY WITH VALID JSON! No additional text or explanation.

For each logical unit, provide:
1. A descriptive name (brief but clear)
2. The files involved
3. A brief explanation of what this change accomplishes (1-2 sentences maximum)
4. Whether it should be split into a separate commit

Output Format:
[
  {{
    "name": "Name of logical unit 1",
    "files": ["file1.py", "file2.py"],
    "explanation": "Brief explanation of what this change does",
    "should_split": true/false
  }},
  // More logical units...
]
"""

CHANGE_SPLITTING_PROMPT = PromptTemplate(
    input_variables=["diff", "analysis"],
    template=CHANGE_SPLITTING_TEMPLATE
)

# Fixed prompt with the example clearly separated
COMMIT_MESSAGE_TEMPLATE = """
You are an expert Git commit message writer. Your job is to analyze code changes and write a concise, informative commit message.

The code changes to analyze are:
```
{change_description}
```

Write ONE conventional commit message for THESE CHANGES.

Available commit types: {commit_types}
Available scopes: {commit_scopes}

Format your message like this:
<type>[(scope)]: <description>

[optional body explaining why the change was made]

Rules:
1. Choose ONE type from: {commit_types}
2. Scope is optional, choose from: {commit_scopes}
3. First line should be < 50 characters
4. Use imperative present tense ("add" not "adds")
5. No period at end of first line
6. Optional body should explain WHY, not HOW

DO NOT:
- Include any "Example:" or "Format:" text
- Add "Commit message:" prefix
- Include any separators (---)
- Make multiple commit messages
- Reply with anything other than the commit message itself

IMPORTANT: YOUR ENTIRE RESPONSE SHOULD BE JUST THE COMMIT MESSAGE. DO NOT INCLUDE COMMENTARY.
"""

COMMIT_MESSAGE_PROMPT = PromptTemplate(
    input_variables=["change_description", "commit_types", "commit_scopes"],
    template=COMMIT_MESSAGE_TEMPLATE
)
