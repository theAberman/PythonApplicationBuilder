import difflib
import os

def read_file(file_path):
    """Read the content of a file and return it as a list of lines."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()

def write_file(file_path, updated_content):
    """Write the updated content to a file after displaying a diff and confirming changes."""
    # Re-read the original content to ensure accuracy
    original_content = read_file(file_path) if os.path.exists(file_path) else []

    # Display the diff
    diff = difflib.unified_diff(original_content, updated_content, fromfile='original', tofile='updated', lineterm='')
    print("\n".join(diff))

    # Ask for user confirmation before writing changes
    if confirm_changes():
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(updated_content)
            f.truncate()
            print(f"[DEBUG] Successfully wrote changes to {file_path}.")
            return True
    else:
        print(f"[DEBUG] Changes to {file_path} rejected by user.")
        return False

def delete_file(file_path):

    print("f[INFO] Deleting file {file_path}")
    # Ask for user confirmation before writing changes
    if confirm_changes():
        with open(file_path, "w", encoding="utf-8") as f:
            os.remove(file_path)
            print(f"[DEBUG] Successfully deleted {file_path}.")
            return True
    else:
        print(f"[DEBUG] Changes to {file_path} rejected by user.")
        return False

def display_diff(original, updated):
    """Display the diff between the original and updated content."""
    diff = difflib.unified_diff(original, updated, fromfile='original', tofile='updated', lineterm='')
    print("\n".join(diff))

def confirm_changes():
    """Ask for user confirmation before writing changes."""
    return input("Do you want to proceed with these changes? (y/n): ").strip().lower() == 'y'
