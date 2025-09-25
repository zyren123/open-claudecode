from langchain_core.tools import tool
import os
from typing import Dict, Any, Annotated

# Import the file tracking function from edittool
try:
    from .edittool import mark_file_as_read, is_file_read
except ImportError:
    # Fallback if edittool is not available
    def mark_file_as_read(file_path: str):
        pass
    
    def is_file_read(file_path: str) -> bool:
        return False


@tool
def write_tool(
    file_path: Annotated[str, "The absolute path to the file to write (must be absolute, not relative)"],
    content: Annotated[str, "The content to write to the file"]
) -> Dict[str, Any]:
    """
    Writes a file to the local filesystem.

Usage:
- This tool will overwrite the existing file if there is one at the provided path.
- If this is an existing file, you MUST use the Read tool first to read the file's contents. This tool will fail if you did not read the file first.
- ALWAYS prefer editing existing files in the codebase. NEVER write new files unless explicitly required.
- NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
- Only use emojis if the user explicitly requests it. Avoid writing emojis to files unless asked.
    """
    try:
        # Validate that path is absolute
        if not os.path.isabs(file_path):
            return {
                "success": False,
                "error": f"Path must be absolute, got relative path: {file_path}",
                "file_path": file_path,
                "content": f"ERROR: Path must be absolute, got relative path: {file_path}"
            }
        
        # Check if file already exists
        file_exists = os.path.exists(file_path)
        
        # Validate that it's not a directory (check this first)
        if file_exists and os.path.isdir(file_path):
            return {
                "success": False,
                "error": f"Path is a directory, not a file: {file_path}",
                "file_path": file_path,
                "content": f"ERROR: Path is a directory, not a file: {file_path}"
            }
        
        # If file exists, check if it has been read in this session
        if file_exists:
            if not is_file_read(file_path):
                return {
                    "success": False,
                    "error": "You must use the Read tool first to read the file's contents before overwriting it. This tool will fail if you did not read the file first.",
                    "file_path": file_path,
                    "existing_file": True,
                    "content": "ERROR: You must use the Read tool first to read the file's contents before overwriting it."
                }
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to create directory {directory}: {str(e)}",
                    "file_path": file_path,
                    "content": f"ERROR: Failed to create directory {directory}: {str(e)}"
                }
        
        # Get original file size if it exists
        original_size = 0
        if file_exists:
            try:
                original_size = os.path.getsize(file_path)
            except Exception:
                original_size = 0
        
        # Write the content to the file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except PermissionError:
            return {
                "success": False,
                "error": f"Permission denied when writing to file: {file_path}",
                "file_path": file_path,
                "content": f"ERROR: Permission denied when writing to file: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to write file: {str(e)}",
                "file_path": file_path,
                "content": f"ERROR: Failed to write file: {str(e)}"
            }
        
        # Get new file size
        try:
            new_size = os.path.getsize(file_path)
        except Exception:
            new_size = 0
        
        # Calculate statistics
        content_lines = len(content.splitlines())
        content_chars = len(content)
        
        # Mark file as read since we just wrote it
        mark_file_as_read(file_path)
        
        return {
            "success": True,
            "message": f"Successfully {'overwrote' if file_exists else 'created'} file: {file_path}",
            "file_path": file_path,
            "file_existed": file_exists,
            "original_size_bytes": original_size,
            "new_size_bytes": new_size,
            "content_lines": content_lines,
            "content_chars": content_chars,
            "operation": "overwrite" if file_exists else "create",
            "content": f"Successfully {'overwrote' if file_exists else 'created'} file: {file_path} ({content_lines} lines, {content_chars} characters)"
        }
        
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: {file_path}",
            "file_path": file_path,
            "content": f"ERROR: Permission denied: {file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "file_path": file_path,
            "content": f"ERROR: Unexpected error: {str(e)}"
        } 