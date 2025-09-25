from langchain_core.tools import tool
import os
import mimetypes
from typing import Dict, Any, Optional, Annotated
import base64

# Import the file tracking function from edittool
try:
    from .edittool import mark_file_as_read
except ImportError:
    # Fallback if edittool is not available
    def mark_file_as_read(file_path: str):
        pass


@tool
def read_tool(
    file_path: Annotated[str, "The absolute path to the file to read"],
    offset: Annotated[Optional[int], "The line number to start reading from. Only provide if the file is too large to read at once"] = None,
    limit: Annotated[Optional[int], "The number of lines to read. Only provide if the file is too large to read at once."] = None
) -> Dict[str, Any]:
    """
    Reads a file from the local filesystem. You can access any file directly by using this tool.
    Assume this tool is able to read all files on the machine. If the User provides a path to a file assume that path is valid. It is okay to read a file that does not exist; an error will be returned.

    Usage:
    - The file_path parameter must be an absolute path, not a relative path
    - By default, it reads up to 2000 lines starting from the beginning of the file
    - You can optionally specify a line offset and limit (especially handy for long files), but it's recommended to read the whole file by not providing these parameters
    - Any lines longer than 2000 characters will be truncated
    - Results are returned using cat -n format, with line numbers starting at 1
    - This tool allows Claude Code to read images (eg PNG, JPG, etc). When reading an image file the contents are presented visually as Claude Code is a multimodal LLM.
    - This tool can read PDF files (.pdf). PDFs are processed page by page, extracting both text and visual content for analysis.
    - For Jupyter notebooks (.ipynb files), use the NotebookRead instead
    - You have the capability to call multiple tools in a single response. It is always better to speculatively read multiple files as a batch that are potentially useful.
    - You will regularly be asked to read screenshots. If the user provides a path to a screenshot ALWAYS use this tool to view the file at the path. This tool will work with all temporary file paths like /var/folders/123/abc/T/TemporaryItems/NSIRD_screencaptureui_ZfB1tD/Screenshot.png
    - If you read a file that exists but has empty contents you will receive a system reminder warning in place of file contents.
    """
    try:
        # Validate that path is absolute
        if not os.path.isabs(file_path):
            return {
                "success": False,
                "content": f"Path must be absolute, got relative path: {file_path}",
                "error": f"Path must be absolute, got relative path: {file_path}",
                "file_path": file_path
            }
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "content": f"File does not exist: {file_path}",
                "error": f"File does not exist: {file_path}",
                "file_path": file_path
            }
        
        # Check if path is a file (not directory)
        if not os.path.isfile(file_path):
            return {
                "success": False,
                "content": f"Path is not a file: {file_path}",
                "error": f"Path is not a file: {file_path}",
                "file_path": file_path
            }
        
        # Get file information
        file_size = os.path.getsize(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Handle empty files
        if file_size == 0:
            mark_file_as_read(file_path)
            return {
                "success": True,
                "content": "*** WARNING: File exists but has empty contents ***",
                "lines_read": 0,
                "total_lines": 0,
                "file_size": 0,
                "file_path": file_path,
                "mime_type": mime_type,
                "truncated": False
            }
        
        # Check if it's an image file
        if mime_type and mime_type.startswith('image/'):
            try:
                with open(file_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                mark_file_as_read(file_path)
                return {
                    "success": True,
                    "content": f"[IMAGE FILE: {file_path}]\nImage content available for multimodal analysis.",
                    "image_data": image_data,
                    "file_size": file_size,
                    "file_path": file_path,
                    "mime_type": mime_type,
                    "is_image": True
                }
            except Exception as e:
                return {
                    "success": False,
                    "content": f"Failed to read image file: {str(e)}",
                    "error": f"Failed to read image file: {str(e)}",
                    "file_path": file_path
                }
        
        # Check if it's a PDF file
        if mime_type == 'application/pdf' or file_path.lower().endswith('.pdf'):
            mark_file_as_read(file_path)
            return {
                "success": True,
                "content": f"[PDF FILE: {file_path}]\nPDF processing requires specialized handling. File size: {file_size} bytes",
                "file_size": file_size,
                "file_path": file_path,
                "mime_type": mime_type,
                "is_pdf": True,
                "note": "PDF files are processed page by page, extracting both text and visual content for analysis."
            }
        
        # Check if it's a Jupyter notebook
        if file_path.lower().endswith('.ipynb'):
            return {
                "success": False,
                "content": "For Jupyter notebooks (.ipynb files), use the NotebookRead tool instead",
                "error": "For Jupyter notebooks (.ipynb files), use the NotebookRead tool instead",
                "file_path": file_path,
                "mime_type": mime_type
            }
        
        # Set default values
        default_limit = 2000
        start_line = max(1, offset or 1)  # 1-based line numbering
        max_lines = limit or default_limit
        
        # Try to read as text file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = []
                current_line = 1
                lines_read = 0
                
                # Skip lines until we reach the start_line
                while current_line < start_line:
                    line = f.readline()
                    if not line:  # End of file
                        break
                    current_line += 1
                
                # Read the requested lines
                while lines_read < max_lines:
                    line = f.readline()
                    if not line:  # End of file
                        break
                    
                    # Remove newline and truncate if too long
                    line_content = line.rstrip('\n\r')
                    if len(line_content) > 2000:
                        line_content = line_content[:2000] + "... [TRUNCATED]"
                    
                    # Format with line number (cat -n format)
                    formatted_line = f"{current_line:6}|{line_content}"
                    lines.append(formatted_line)
                    
                    current_line += 1
                    lines_read += 1
                
                # Check if there are more lines (for truncation info)
                next_line = f.readline()
                has_more_lines = bool(next_line)
                
                # Get total line count efficiently
                if not has_more_lines and start_line == 1:
                    total_lines = current_line - 1
                else:
                    # Count total lines in file
                    f.seek(0)
                    total_lines = sum(1 for _ in f)
        
        except UnicodeDecodeError:
            # Try binary mode for non-text files
            try:
                with open(file_path, 'rb') as f:
                    binary_data = f.read(1024)  # Read first 1KB
                mark_file_as_read(file_path)
                return {
                    "success": True,
                    "content": f"[BINARY FILE: {file_path}]\nFirst 1KB of binary data (base64 encoded):\n{base64.b64encode(binary_data).decode('utf-8')}",
                    "file_size": file_size,
                    "file_path": file_path,
                    "mime_type": mime_type,
                    "is_binary": True
                }
            except Exception as e:
                return {
                    "success": False,
                    "content": f"Failed to read binary file: {str(e)}",
                    "error": f"Failed to read binary file: {str(e)}",
                    "file_path": file_path
                }
        
        content = '\n'.join(lines)
        truncated = has_more_lines if 'has_more_lines' in locals() else False
        
        mark_file_as_read(file_path)
        return {
            "success": True,
            "content": content,
            "lines_read": len(lines),
            "total_lines": total_lines if 'total_lines' in locals() else None,
            "start_line": start_line,
            "file_size": file_size,
            "file_path": file_path,
            "mime_type": mime_type,
            "truncated": truncated,
            "offset_used": offset,
            "limit_used": max_lines
        }
        
    except PermissionError:
        return {
            "success": False,
            "content": f"Permission denied: {file_path}",
            "error": f"Permission denied: {file_path}",
            "file_path": file_path
        }
    except Exception as e:
        return {
            "success": False,
            "content": f"Unexpected error: {str(e)}",
            "error": f"Unexpected error: {str(e)}",
            "file_path": file_path
        } 