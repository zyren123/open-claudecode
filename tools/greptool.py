from langchain_core.tools import tool
import subprocess
import os
import shutil
from typing import Dict, Any, Optional, Annotated, Literal


@tool
def grep_tool(
    pattern: Annotated[str, "The regular expression pattern to search for in file contents"],
    path: Annotated[Optional[str], "File or directory to search in (rg PATH). Defaults to current working directory."] = None,
    glob: Annotated[Optional[str], "Glob pattern to filter files (e.g. \"*.js\", \"*.{ts,tsx}\") - maps to rg --glob"] = None,
    output_mode: Annotated[
        Literal["content", "files_with_matches", "count"], 
        "Output mode: \"content\" shows matching lines (supports -A/-B/-C context, -n line numbers, head_limit), \"files_with_matches\" shows file paths (supports head_limit), \"count\" shows match counts (supports head_limit). Defaults to \"files_with_matches\"."
    ] = "files_with_matches",
    B: Annotated[Optional[int], "Number of lines to show before each match (rg -B). Requires output_mode: \"content\", ignored otherwise."] = None,
    A: Annotated[Optional[int], "Number of lines to show after each match (rg -A). Requires output_mode: \"content\", ignored otherwise."] = None,
    C: Annotated[Optional[int], "Number of lines to show before and after each match (rg -C). Requires output_mode: \"content\", ignored otherwise."] = None,
    n: Annotated[Optional[bool], "Show line numbers in output (rg -n). Requires output_mode: \"content\", ignored otherwise."] = None,
    i: Annotated[Optional[bool], "Case insensitive search (rg -i)"] = None,
    type: Annotated[Optional[str], "File type to search (rg --type). Common types: js, py, rust, go, java, etc. More efficient than include for standard file types."] = None,
    head_limit: Annotated[Optional[int], "Limit output to first N lines/entries, equivalent to \"| head -N\". Works across all output modes: content (limits output lines), files_with_matches (limits file paths), count (limits count entries). When unspecified, shows all results from ripgrep."] = None,
    multiline: Annotated[Optional[bool], "Enable multiline mode where . matches newlines and patterns can span lines (rg -U --multiline-dotall). Default: false."] = None
) -> Dict[str, Any]:
    """
    A powerful search tool built on ripgrep  
    Usage:
    - ALWAYS use Grep for search tasks. NEVER invoke `grep` or `rg` as a Bash command. The Grep tool has been optimized for correct permissions and access.
    - Supports full regex syntax (e.g., \"log.*Error\", \"function\\s+\\w+\")
    - Filter files with glob parameter (e.g., \"*.js\", \"**/*.tsx\") or type parameter (e.g., \"js\", \"py\", \"rust\")
    - Output modes: \"content\" shows matching lines, \"files_with_matches\" shows only file paths (default), \"count\" shows match counts
    - Use Task tool for open-ended searches requiring multiple rounds
    - Pattern syntax: Uses ripgrep (not grep) - literal braces need escaping (use `interface\\{\\}` to find `interface{}` in Go code)
    - Multiline matching: By default patterns match within single lines only. For cross-line patterns like `struct \\{[\\s\\S]*?field`, use `multiline: true`
    """
    
    try:
        # Check which grep tool is available
        use_ripgrep = shutil.which("rg") is not None
        use_grep = shutil.which("grep") is not None
        
        if not use_ripgrep and not use_grep:
            return {
                "success": False,
                "error": "Neither ripgrep (rg) nor grep found on system",
                "pattern": pattern,
                "command": "rg/grep not available",
                "content": "ERROR: Neither ripgrep (rg) nor grep found on system"
            }
        
        # Build command based on available tool
        if use_ripgrep:
            cmd = ["rg"]
            cmd.append(pattern)
        else:
            # Fallback to standard grep
            cmd = ["grep", "-r"]
            if i:
                cmd.append("-i")
            cmd.append(pattern)
        
        # Add path if specified, otherwise default to current directory  
        if path:
            if not os.path.exists(path):
                return {
                    "success": False,
                    "error": f"Path does not exist: {path}",
                    "pattern": pattern,
                    "command": " ".join(cmd),
                    "content": f"ERROR: Path does not exist: {path}"
                }
            cmd.append(path)
        
        if use_ripgrep:
            # Full ripgrep functionality
            # Output mode handling - this eliminates special cases
            output_flags = {
                "files_with_matches": ["-l"],
                "count": ["-c"], 
                "content": []  # Default ripgrep behavior
            }
            
            if output_mode not in output_flags:
                return {
                    "success": False,
                    "error": f"Invalid output_mode: {output_mode}. Must be one of: {list(output_flags.keys())}",
                    "pattern": pattern,
                    "command": " ".join(cmd),
                    "content": f"ERROR: Invalid output_mode: {output_mode}. Must be one of: {list(output_flags.keys())}"
                }
                
            cmd.extend(output_flags[output_mode])
            
            # Context options (only valid for content mode)
            if output_mode == "content":
                if C is not None:
                    cmd.extend(["-C", str(C)])
                else:
                    if B is not None:
                        cmd.extend(["-B", str(B)])
                    if A is not None:
                        cmd.extend(["-A", str(A)])
                
                if n:
                    cmd.append("-n")
            
            # Ripgrep-specific flags
            if i:
                cmd.append("-i")
                
            if multiline:
                cmd.extend(["--multiline", "-U"])
            
            # Additional options
            if glob:
                cmd.extend(["--glob", glob])
                
            if type:
                cmd.extend(["--type", type])
        else:
            # Standard grep - limited functionality
            if output_mode == "files_with_matches":
                cmd.append("-l")
            elif output_mode == "count":
                cmd.append("-c")
            elif output_mode == "content":
                if n:
                    cmd.append("-n")
                if C is not None:
                    cmd.extend(["-C", str(C)])
                elif B is not None:
                    cmd.extend(["-B", str(B)])
                elif A is not None:
                    cmd.extend(["-A", str(A)])
            
            # Add current directory if no path specified
            if not path:
                cmd.append(".")
                
            # Note: grep doesn't support glob, type, or multiline the same way
            
        # Execute search command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,  # Reasonable timeout for searches
            cwd=os.getcwd()
        )
        
        output = result.stdout.strip()
        error_output = result.stderr.strip()
        
        # Apply head limit if specified
        if head_limit and output:
            lines = output.split('\n')
            if len(lines) > head_limit:
                output = '\n'.join(lines[:head_limit])
                truncated = True
            else:
                truncated = False
        else:
            truncated = False
        
        # Parse results based on output mode
        if output_mode == "files_with_matches":
            files = output.split('\n') if output else []
            files = [f for f in files if f.strip()]  # Remove empty lines
            
            return {
                "success": True,
                "files": files,
                "count": len(files),
                "pattern": pattern,
                "output_mode": output_mode,
                "truncated": truncated,
                "tool_used": "ripgrep" if use_ripgrep else "grep",
                "command": " ".join(cmd),
                "content": f"Found {len(files)} files matching pattern '{pattern}'"
            }
            
        elif output_mode == "count":
            # Parse count output (file:count format)
            counts = {}
            if output:
                for line in output.split('\n'):
                    if line.strip() and ':' in line:
                        parts = line.rsplit(':', 1)
                        if len(parts) == 2:
                            file_path, count_str = parts
                            try:
                                counts[file_path] = int(count_str)
                            except ValueError:
                                continue
            
            total_matches = sum(counts.values())
            
            return {
                "success": True,
                "file_counts": counts,
                "total_matches": total_matches,
                "total_files": len(counts),
                "pattern": pattern,
                "output_mode": output_mode,
                "truncated": truncated,
                "tool_used": "ripgrep" if use_ripgrep else "grep",
                "command": " ".join(cmd),
                "content": f"Found {total_matches} matches in {len(counts)} files for pattern '{pattern}'"
            }
            
        else:  # content mode
            return {
                "success": True,
                "content": output if output else f"No matches found for pattern '{pattern}'",
                "pattern": pattern,
                "output_mode": output_mode,
                "truncated": truncated,
                "tool_used": "ripgrep" if use_ripgrep else "grep",
                "error": error_output if error_output else None,
                "command": " ".join(cmd)
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Search timed out after 30 seconds",
            "pattern": pattern,
            "command": " ".join(cmd) if 'cmd' in locals() else "rg " + pattern,
            "content": "ERROR: Search timed out after 30 seconds"
        }
    except subprocess.SubprocessError as e:
        return {
            "success": False,
            "error": f"Subprocess error: {str(e)}",
            "pattern": pattern,
            "command": " ".join(cmd) if 'cmd' in locals() else "rg " + pattern,
            "content": f"ERROR: Subprocess error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "pattern": pattern,
            "command": " ".join(cmd) if 'cmd' in locals() else "rg " + pattern,
            "content": f"ERROR: Unexpected error: {str(e)}"
        }
