from langchain_core.tools import tool
import glob
import os
from typing import Dict, Any, Optional, Annotated


@tool
def glob_tool(
    pattern: Annotated[str, "The glob pattern to match files against"],
    path: Annotated[Optional[str], "The directory to search in. If not specified, the current working directory will be used. IMPORTANT: Omit this field to use the default directory. DO NOT enter \"undefined\" or \"null\" - simply omit it for the default behavior. Must be a valid directory path if provided."] = None
) -> Dict[str, Any]:
    """
    - Fast file pattern matching tool that works with any codebase size.
    - Supports glob patterns like "**/*.js" or "src/**/*.ts"
    - Returns matching file paths sorted by modification time
    - Use this tool when you need to find files by name patterns

    - When you are doing an open ended search that may require multiple rounds of
    globbing and grepping, use the Agent tool instead

    - You have the capability to call multiple tools in a single response. It is
    always better to speculatively perform multiple searches as a batch that are
    potentially useful.
    """
    try:
        # Set the search directory
        search_dir = path if path is not None else os.getcwd()
        
        # Validate that the path exists if provided
        if path is not None and not os.path.isdir(path):
            return {
                "success": False,
                "files": [],
                "error": f"Directory does not exist: {path}",
                "pattern": pattern,
                "search_directory": search_dir,
                "content": f"ERROR: Directory does not exist: {path}"
            }
        
        # Save current directory and change to search directory
        original_cwd = os.getcwd()
        try:
            os.chdir(search_dir)
            
            # Use glob to find matching files
            # glob.glob with recursive=True supports ** patterns
            matched_files = glob.glob(pattern, recursive=True)
            
            # Filter out directories, keep only files
            file_paths = [f for f in matched_files if os.path.isfile(f)]
            
            # Convert to absolute paths and get modification times
            files_with_mtime = []
            for file_path in file_paths:
                abs_path = os.path.abspath(file_path)
                try:
                    mtime = os.path.getmtime(abs_path)
                    files_with_mtime.append((abs_path, mtime))
                except OSError:
                    # File might have been deleted between glob and stat
                    continue
            
            # Sort by modification time (newest first)
            files_with_mtime.sort(key=lambda x: x[1], reverse=True)
            
            # Extract just the file paths
            sorted_files = [file_path for file_path, _ in files_with_mtime]
            
            return {
                "success": True,
                "files": sorted_files,
                "count": len(sorted_files),
                "pattern": pattern,
                "search_directory": search_dir,
                "content": f"Found {len(sorted_files)} files matching pattern '{pattern}' in {search_dir}"
            }
            
        finally:
            # Always restore original directory
            os.chdir(original_cwd)
            
    except Exception as e:
        return {
            "success": False,
            "files": [],
            "error": f"Glob search failed: {str(e)}",
            "pattern": pattern,
            "search_directory": search_dir if 'search_dir' in locals() else "unknown",
            "content": f"ERROR: Glob search failed: {str(e)}"
        }
