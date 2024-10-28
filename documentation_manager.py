import os
from file_io import read_file, write_file

SUMMARY_PREFIX = "Application Builder File Summary"
README_FILE = "README.md"
README_PROMPT = (
    "You are tasked with generating a **README.md** for a Python project based on the following analysis. "
    "The README should concisely convey the essential information to users and developers.\n\n"

    "Below is the **analysis result** of the project:\n\n"
    "{application_overview}\n\n"

    "Please generate the following sections:\n"
    "1. **Project Title**: Extract from the overview if available.\n"
    "2. **Description**: Provide a concise summary of the project's purpose and scope.\n"
    "3. **Installation**: If relevant, include any setup or installation instructions.\n"
    "4. **Usage**: Explain how to run or use the project, mentioning key scripts or commands.\n"
    "5. **Features**: Summarize the main features based on the provided analysis.\n"

    "Format the README as **Markdown**. Ensure that it is readable and well-structured.  Ensure that what you generate can be directly inserted into the file.\n\n"

    "Now, generate the README using the provided analysis."
)
FILE_OVERVIEW_PROMPT = (
    "You are tasked with generating a **file overview comment block** for a Python file, based on the following insights.\n\n"

    "Below are the **insights** for this file:\n\n"
    "{file_insights}\n\n"

    "Please generate a concise file overview, formatted as a **multiline comment**."
    "Ensure that what you generate can be directly inserted into the code without further modification."
    "The first line of the comment block should be the following string:\n"
    f"\"{SUMMARY_PREFIX}\"\n\n"

    "The overview should include:\n"
    "1. **File Purpose**: Describe what the file does and how it fits into the project.\n"
    "2. **Key Components**: List major functions or classes and briefly explain their roles.\n"
    "3. **Dependencies**: Mention key libraries or internal modules used within the file.\n"
    "4. **Usage Context**: If applicable, describe how this file is invoked or integrated into the project workflow.\n\n"

    "Format the block using triple quotes (`\"\"\"`).\n"
    "Example:\n"
    "```python\n"
    "\"\"\"\n"
    f"{SUMMARY_PREFIX}\n\n"
    "This file handles [brief description].\n\n"
    "Key Components:\n"
    "- **function_a()**: [description]\n"
    "- **ClassB**: [description]\n\n"
    "Dependencies:\n"
    "- `os`, `sys`: Standard Python libraries.\n"
    "Usage:\n"
    "This file is invoked by [explanation].\n"
    "\"\"\"\n"
    "```\n\n"

    "Now, generate the file overview using the provided insights."
)



class DocumentationManager:
    """Manage documentation updates, including comments and README files."""
    def __init__(self, chatgpt_client):
        self.chatgpt_client = chatgpt_client

    def maintain_comments(self, analysis_result, path):
        """Update comments across the project using the provided analysis."""
        print("[DEBUG] Updating comments...")
        for file_summary in analysis_result["file_summaries"]:
            self.update_file_comment(file_summary["file"], file_summary["summary"], path)

    def update_file_comment(self, file_name, file_summary, path):
        """Update or add comments in a given file based on the analysis."""
        file_path = os.path.join(path, file_name)
        try:
            content = read_file(file_path)
            cleaned_content = clear_file_comment(content)
            file_overview = self.generate_file_overview(file_name, file_summary)
            updated_content = file_overview + cleaned_content

            if write_file(file_path, updated_content):
                print(f"[DEBUG] Comments updated in {file_name}.")
            else:
                print(f"[DEBUG] Changes were not written to {file_name}.")

        except Exception as e:
            print(f"❌ [DEBUG] Error updating {file_path}: {e}")

    def generate_file_overview(self, file_name, file_insights):
        """Generate a file overview using the ChatGPT client."""
        prompt = FILE_OVERVIEW_PROMPT.format(file_name=file_name, file_insights=file_insights)
        return self.chatgpt_client.fetch_chatgpt_response(prompt)

    def add_function_comment(self, file, function_comment):
        """Add a comment to the specified function in the file."""
        file_path = os.path.join(self.path, file)
        try:
            content = read_file(file_path)
            for i, line in enumerate(content):
                if line.startswith("def "):  # Identify function definition lines
                    if not any(function_comment in existing for existing in content[i-1:i+2]):
                        content.insert(i, f"{function_comment}\n")  # Add the function comment
                    break
            write_file(file_path, content)
            print(f"[DEBUG] Function comment added to {file}: {function_comment}")
        except Exception as e:
            print(f"❌ [DEBUG] Error adding function comment to {file}: {e}")

    def update_readme(self, analysis_result, directory):
        """Update or generate the README.md file based on the analysis."""
        overall_insight = analysis_result["overall_insight"]

        if os.path.exists(README_FILE):
            readme_content = read_file(README_FILE)
            if overall_insight not in readme_content:
                if write_file(README_FILE, [overall_insight]):
                    print("✅ README.md has been updated.")
                else:
                    print("[DEBUG] README update skipped.")
            else:
                print("✅ README.md is already up-to-date.")
        else:
            if write_file(README_FILE, [overall_insight]):
                print("✅ README.md created.")

def clear_file_comment(content):
    """
    Clear the existing system-generated file comment based on the SUMMARY_PREFIX,
    stopping at the first import statement. Handles multiline comments, including
    those that start and end on the same line.
    """
    updated_content = []
    multiline_comment_active = False
    summary_comment_found = False
    ongoing_multiline_comment = []

    for line in content:
        # Detect and stop processing at the first import statement
        if line.strip().startswith("import ") or line.strip().startswith("from "):
            updated_content.append(line)
            updated_content.extend(content[content.index(line) + 1:])  # Add remaining content
            break

        # Handle single-line multiline comments
        if line.strip().startswith('"""') and line.strip().endswith('"""'):
            if SUMMARY_PREFIX in line:
                summary_comment_found = True  # Mark it found and skip
                continue  # Skip the entire single-line comment
            else:
                updated_content.append(line)
                continue

        # Check for the start or end of a multiline comment block
        if line.strip().startswith('"""'):
            multiline_comment_active = not multiline_comment_active

            if multiline_comment_active:
                ongoing_multiline_comment = [line]  # Start collecting
                continue  # Skip the start of the comment

            # If we're ending the comment block
            if summary_comment_found:
                summary_comment_found = False  # Reset state
                ongoing_multiline_comment = []  # Discard the comment
                continue  # Skip the end marker

            # If it's not our summary comment, keep it
            updated_content.extend(ongoing_multiline_comment)
            ongoing_multiline_comment = []
            continue

        # Collect lines inside a multiline comment block
        if multiline_comment_active:
            ongoing_multiline_comment.append(line)

            if SUMMARY_PREFIX in line:
                summary_comment_found = True  # Mark it found
            continue  # Skip further processing

        # Append non-comment lines directly to the updated content
        updated_content.append(line)

    return updated_content

