from langchain_core.tools import tool
from typing import Dict, Any, Annotated
import os

# Track files that have been read during this session
_read_files_tracker = set()

def mark_file_as_read(file_path: str):
    """Mark a file as having been read in this session."""
    _read_files_tracker.add(os.path.abspath(file_path))

def is_file_read(file_path: str) -> bool:
    """Check if a file has been read in this session."""
    return os.path.abspath(file_path) in _read_files_tracker


@tool
def edit_tool(
    file_path: Annotated[str, "The absolute path to the file to modify"],
    old_string: Annotated[str, "The text to replace"], 
    new_string: Annotated[str, "The text to replace it with (must be different from old_string)"],
    replace_all: Annotated[bool, "Replace all occurences of old_string (default false)"] = False
) -> Dict[str, Any]:
    """
    Performs exact string replacements in files.

    Usage:
    - You must use your `Read` tool at least once in the conversation before editing. This tool will error if you attempt an edit without reading the file.
    - When editing text from Read tool output, ensure you preserve the exact indentation (tabs/spaces) as it appears AFTER the line number prefix. The line number prefix format is: spaces + line number + tab. Everything after that tab is the actual file content to match. Never include any part of the line number prefix in the old_string or new_string.
    - ALWAYS prefer editing existing files in the codebase. NEVER write new files unless explicitly required.
    - Only use emojis if the user explicitly requests it. Avoid adding emojis to files unless asked.
    - The edit will FAIL if `old_string` is not unique in the file. Either provide a larger string with more surrounding context to make it unique or use `replace_all` to change every instance of `old_string`.
    - Use `replace_all` for replacing and renaming strings across the file. This parameter is useful if you want to rename a variable for instance.
    """
    try:
        # Validate that old_string and new_string are different
        if old_string == new_string:
            return {
                "success": False,
                "error": "old_string and new_string must be different",
                "file_path": file_path,
                "old_string": old_string[:100] + "..." if len(old_string) > 100 else old_string,
                "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
                "content": "ERROR: old_string and new_string must be different"
            }
        
        # Validate that path is absolute
        if not os.path.isabs(file_path):
            return {
                "success": False,
                "error": f"Path must be absolute, got relative path: {file_path}",
                "file_path": file_path,
                "old_string": old_string[:100] + "..." if len(old_string) > 100 else old_string,
                "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
                "content": f"ERROR: Path must be absolute, got relative path: {file_path}"
            }
        
        # Check if file has been read in this session
        if not is_file_read(file_path):
            return {
                "success": False,
                "error": "You must use your Read tool at least once before editing this file. Please read the file first to understand its content.",
                "file_path": file_path,
                "old_string": old_string[:100] + "..." if len(old_string) > 100 else old_string,
                "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
                "content": "ERROR: You must use your Read tool at least once before editing this file. Please read the file first to understand its content."
            }
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File does not exist: {file_path}",
                "file_path": file_path,
                "old_string": old_string[:100] + "..." if len(old_string) > 100 else old_string,
                "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
                "content": f"ERROR: File does not exist: {file_path}"
            }
        
        # Check if path is a file (not directory)
        if not os.path.isfile(file_path):
            return {
                "success": False,
                "error": f"Path is not a file: {file_path}",
                "file_path": file_path,
                "old_string": old_string[:100] + "..." if len(old_string) > 100 else old_string,
                "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
                "content": f"ERROR: Path is not a file: {file_path}"
            }
        
        # Read the file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": f"File is not a text file or has encoding issues: {file_path}",
                "file_path": file_path,
                "old_string": old_string[:100] + "..." if len(old_string) > 100 else old_string,
                "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
                "content": f"ERROR: File is not a text file or has encoding issues: {file_path}"
            }
        
        # Check if old_string exists in the file
        if old_string not in original_content:
            return {
                "success": False,
                "error": f"old_string not found in file. Make sure the string matches exactly, including whitespace and indentation.",
                "file_path": file_path,
                "old_string": old_string[:200] + "..." if len(old_string) > 200 else old_string,
                "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
                "suggestion": "Try using a larger string with more surrounding context to make it unique, or check your Read tool output for exact formatting.",
                "content": f"ERROR: old_string not found in file. Make sure the string matches exactly, including whitespace and indentation."
            }
        
        # Count occurrences of old_string
        occurrence_count = original_content.count(old_string)
        
        # If not replace_all and multiple occurrences, fail
        if not replace_all and occurrence_count > 1:
            return {
                "success": False,
                "error": f"old_string appears {occurrence_count} times in the file. Either provide a larger string with more surrounding context to make it unique or use replace_all=True to change every instance.",
                "file_path": file_path,
                "old_string": old_string[:200] + "..." if len(old_string) > 200 else old_string,
                "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
                "occurrences": occurrence_count,
                "content": f"ERROR: old_string appears {occurrence_count} times in the file. Either provide a larger string with more surrounding context to make it unique or use replace_all=True to change every instance."
            }
        
        # Perform the replacement
        if replace_all:
            new_content = original_content.replace(old_string, new_string)
            replacements_made = occurrence_count
        else:
            # Replace only the first occurrence
            new_content = original_content.replace(old_string, new_string, 1)
            replacements_made = 1
        
        # Write the updated content back to the file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except PermissionError:
            return {
                "success": False,
                "error": f"Permission denied when writing to file: {file_path}",
                "file_path": file_path,
                "old_string": old_string[:100] + "..." if len(old_string) > 100 else old_string,
                "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
                "content": f"ERROR: Permission denied when writing to file: {file_path}"
            }
        
        # Calculate statistics
        original_lines = len(original_content.splitlines())
        new_lines = len(new_content.splitlines())
        lines_changed = abs(new_lines - original_lines)
        
        return {
            "success": True,
            "message": f"Successfully {'replaced all' if replace_all else 'replaced'} {replacements_made} occurrence(s) of the specified string",
            "file_path": file_path,
            "replacements_made": replacements_made,
            "total_occurrences_found": occurrence_count,
            "replace_all_used": replace_all,
            "original_lines": original_lines,
            "new_lines": new_lines,
            "lines_changed": lines_changed,
            "file_size_bytes": len(new_content.encode('utf-8')),
            "old_string_preview": old_string[:100] + "..." if len(old_string) > 100 else old_string,
            "new_string_preview": new_string[:100] + "..." if len(new_string) > 100 else new_string,
            "content": f"Successfully {'replaced all' if replace_all else 'replaced'} {replacements_made} occurrence(s) of the specified string in {file_path}"
        }
        
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: {file_path}",
            "file_path": file_path,
            "old_string": old_string[:100] + "..." if len(old_string) > 100 else old_string,
            "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
            "content": f"ERROR: Permission denied: {file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "file_path": file_path,
            "old_string": old_string[:100] + "..." if len(old_string) > 100 else old_string,
            "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
            "content": f"ERROR: Unexpected error: {str(e)}"
        } 