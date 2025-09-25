from langchain_core.tools import tool
import os
import fnmatch
from typing import Dict, Any, List, Optional, Annotated


@tool
def ls_tool(
    path: Annotated[str, "The absolute path to the directory to list (must be absolute, not relative)"],
    ignore: Annotated[Optional[List[str]], "List of glob patterns to ignore"] = None
) -> Dict[str, Any]:
    """
    Lists files and directories in a given path. The path parameter must be an absolute path, not a relative path. 
    You can optionally provide an array of glob patterns to ignore with the ignore parameter. 
    You should generally prefer the Glob and Grep tools, if you know which directories to search.
    
    Args:
        path: The absolute path to the directory to list (must be absolute, not relative)
        ignore: List of glob patterns to ignore (optional)
    
    Returns:
        Dictionary with success status, list of entries, and metadata
    """
    try:
        # Validate that path is absolute
        if not os.path.isabs(path):
            return {
                "success": False,
                "entries": [],
                "error": f"Path must be absolute, got relative path: {path}",
                "path": path,
                "content": f"ERROR: Path must be absolute, got relative path: {path}"
            }
        
        # Check if path exists
        if not os.path.exists(path):
            return {
                "success": False,
                "entries": [],
                "error": f"Path does not exist: {path}",
                "path": path,
                "content": f"ERROR: Path does not exist: {path}"
            }
        
        # Check if path is a directory
        if not os.path.isdir(path):
            return {
                "success": False,
                "entries": [],
                "error": f"Path is not a directory: {path}",
                "path": path,
                "content": f"ERROR: Path is not a directory: {path}"
            }
        
        # List directory contents
        try:
            all_entries = os.listdir(path)
        except PermissionError:
            return {
                "success": False,
                "entries": [],
                "error": f"Permission denied: {path}",
                "path": path,
                "content": f"ERROR: Permission denied: {path}"
            }
        
        # Filter entries using ignore patterns if provided
        filtered_entries = []
        ignore_patterns = ignore or []
        
        for entry in all_entries:
            # Check if entry matches any ignore pattern
            should_ignore = False
            for pattern in ignore_patterns:
                if fnmatch.fnmatch(entry, pattern):
                    should_ignore = True
                    break
            
            if not should_ignore:
                # Get full path for additional info
                full_path = os.path.join(path, entry)
                try:
                    is_dir = os.path.isdir(full_path)
                    is_file = os.path.isfile(full_path)
                    
                    filtered_entries.append({
                        "name": entry,
                        "path": full_path,
                        "type": "directory" if is_dir else "file" if is_file else "other"
                    })
                except (OSError, PermissionError):
                    # If we can't stat the entry, include it as unknown type
                    filtered_entries.append({
                        "name": entry,
                        "path": full_path,
                        "type": "unknown"
                    })
        
        # Sort entries by name for consistent output
        filtered_entries.sort(key=lambda x: x["name"])
        
        # Separate files and directories for summary
        files = [e for e in filtered_entries if e["type"] == "file"]
        directories = [e for e in filtered_entries if e["type"] == "directory"]
        other = [e for e in filtered_entries if e["type"] in ("other", "unknown")]
        
        return {
            "success": True,
            "entries": filtered_entries,
            "count": len(filtered_entries),
            "summary": {
                "files": len(files),
                "directories": len(directories),
                "other": len(other)
            },
            "path": path,
            "ignore_patterns": ignore_patterns,
            "content": f"Listed {len(filtered_entries)} entries in {path}: {len(files)} files, {len(directories)} directories"
        }
        
    except Exception as e:
        return {
            "success": False,
            "entries": [],
            "error": f"Unexpected error: {str(e)}",
            "path": path,
            "content": f"ERROR: Unexpected error: {str(e)}"
        }
