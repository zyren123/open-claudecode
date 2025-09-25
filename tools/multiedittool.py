from langchain_core.tools import tool
import os
from typing import Dict, Any, List, Annotated
from .edittool import is_file_read

@tool
def multi_edit_tool(
    file_path: Annotated[str, "The absolute path to the file to modify"],
    edits: Annotated[List[Dict[str, Any]], "Array of edit operations to perform sequentially on the file"]
) -> Dict[str, Any]:
    """
    This is a tool for making multiple edits to a single file in one operation. It is built on top of the Edit tool and allows you to perform multiple find-and-replace operations efficiently. Prefer this tool over the Edit tool when you need to make multiple edits to the same file.

Before using this tool:

1. Use the Read tool to understand the file's contents and context
2. Verify the directory path is correct

To make multiple file edits, provide the following:
1. file_path: The absolute path to the file to modify (must be absolute, not relative)
2. edits: An array of edit operations to perform, where each edit contains:
   - old_string: The text to replace (must match the file contents exactly, including all whitespace and indentation)
   - new_string: The edited text to replace the old_string
   - replace_all: Replace all occurences of old_string. This parameter is optional and defaults to false.

IMPORTANT:
- All edits are applied in sequence, in the order they are provided
- Each edit operates on the result of the previous edit
- All edits must be valid for the operation to succeed - if any edit fails, none will be applied
- This tool is ideal when you need to make several changes to different parts of the same file
- For Jupyter notebooks (.ipynb files), use the NotebookEdit instead

CRITICAL REQUIREMENTS:
1. All edits follow the same requirements as the single Edit tool
2. The edits are atomic - either all succeed or none are applied
3. Plan your edits carefully to avoid conflicts between sequential operations

WARNING:
- The tool will fail if edits.old_string doesn't match the file contents exactly (including whitespace)
- The tool will fail if edits.old_string and edits.new_string are the same
- Since edits are applied in sequence, ensure that earlier edits don't affect the text that later edits are trying to find

When making edits:
- Ensure all edits result in idiomatic, correct code
- Do not leave the code in a broken state
- Always use absolute file paths (starting with /)
- Only use emojis if the user explicitly requests it. Avoid adding emojis to files unless asked.
- Use replace_all for replacing and renaming strings across the file. This parameter is useful if you want to rename a variable for instance.

If you want to create a new file, use:
- A new file path, including dir name if needed
- First edit: empty old_string and the new file's contents as new_string
- Subsequent edits: normal edit operations on the created content
    """
    try:
        # Validate input parameters
        if not edits:
            return {
                "success": False,
                "error": "No edits provided. At least one edit operation is required.",
                "file_path": file_path,
                "edits_processed": 0,
                "total_edits": 0,
                "content": "ERROR: No edits provided. At least one edit operation is required."
            }

        # Validate that path is absolute
        if not os.path.isabs(file_path):
            return {
                "success": False,
                "error": f"Path must be absolute, got relative path: {file_path}",
                "file_path": file_path,
                "edits_processed": 0,
                "total_edits": len(edits),
                "content": f"ERROR: Path must be absolute, got relative path: {file_path}"
            }

        # Special case: creating a new file
        creating_new_file = False
        if edits[0].get('old_string') == '':
            creating_new_file = True
            if os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"Cannot create new file: file already exists at {file_path}",
                    "file_path": file_path,
                    "edits_processed": 0,
                    "total_edits": len(edits),
                    "content": f"ERROR: Cannot create new file: file already exists at {file_path}"
                }
        else:
            # For existing files, check standard requirements
            
            # Check if file has been read in this session
            if not is_file_read(file_path):
                return {
                    "success": False,
                    "error": "You must use your Read tool at least once before editing this file. Please read the file first to understand its content.",
                    "file_path": file_path,
                    "edits_processed": 0,
                    "total_edits": len(edits),
                    "content": "ERROR: You must use your Read tool at least once before editing this file. Please read the file first to understand its content."
                }
            
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File does not exist: {file_path}",
                    "file_path": file_path,
                    "edits_processed": 0,
                    "total_edits": len(edits),
                    "content": f"ERROR: File does not exist: {file_path}"
                }
            
            # Check if path is a file (not directory)
            if not os.path.isfile(file_path):
                return {
                    "success": False,
                    "error": f"Path is not a file: {file_path}",
                    "file_path": file_path,
                    "edits_processed": 0,
                    "total_edits": len(edits),
                    "content": f"ERROR: Path is not a file: {file_path}"
                }

        # Read the original file content (if file exists)
        if creating_new_file:
            current_content = ""
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
            except UnicodeDecodeError:
                return {
                    "success": False,
                    "error": f"File is not a text file or has encoding issues: {file_path}",
                    "file_path": file_path,
                    "edits_processed": 0,
                    "total_edits": len(edits),
                    "content": f"ERROR: File is not a text file or has encoding issues: {file_path}"
                }

        # Validate all edits before applying any
        for i, edit in enumerate(edits):
            old_string = edit.get('old_string', '')
            new_string = edit.get('new_string', '')
            replace_all = edit.get('replace_all', False)

            # Validate that old_string and new_string are different (unless creating new file with empty old_string)
            if old_string == new_string and not (creating_new_file and i == 0 and old_string == ''):
                return {
                    "success": False,
                    "error": f"Edit {i+1}: old_string and new_string must be different",
                    "file_path": file_path,
                    "edits_processed": 0,
                    "total_edits": len(edits),
                    "failed_edit": i + 1,
                    "old_string": old_string[:100] + "..." if len(old_string) > 100 else old_string,
                    "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
                    "content": f"ERROR: Edit {i+1}: old_string and new_string must be different"
                }

            # For new file creation, skip content validation for first edit
            if creating_new_file and i == 0 and old_string == '':
                continue

            # Check if old_string exists in current content
            if old_string not in current_content:
                return {
                    "success": False,
                    "error": f"Edit {i+1}: old_string not found in file. Make sure the string matches exactly, including whitespace and indentation.",
                    "file_path": file_path,
                    "edits_processed": 0,
                    "total_edits": len(edits),
                    "failed_edit": i + 1,
                    "old_string": old_string[:200] + "..." if len(old_string) > 200 else old_string,
                    "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
                    "suggestion": "Try using a larger string with more surrounding context to make it unique, or check your Read tool output for exact formatting.",
                    "content": f"ERROR: Edit {i+1}: old_string not found in file. Make sure the string matches exactly, including whitespace and indentation."
                }

            # Count occurrences and validate uniqueness if not replace_all
            occurrence_count = current_content.count(old_string)
            if not replace_all and occurrence_count > 1:
                return {
                    "success": False,
                    "error": f"Edit {i+1}: old_string appears {occurrence_count} times in the file. Either provide a larger string with more surrounding context to make it unique or use replace_all=True to change every instance.",
                    "file_path": file_path,
                    "edits_processed": 0,
                    "total_edits": len(edits),
                    "failed_edit": i + 1,
                    "old_string": old_string[:200] + "..." if len(old_string) > 200 else old_string,
                    "new_string": new_string[:100] + "..." if len(new_string) > 100 else new_string,
                    "occurrences": occurrence_count,
                    "content": f"ERROR: Edit {i+1}: old_string appears {occurrence_count} times in the file. Either provide a larger string with more surrounding context to make it unique or use replace_all=True to change every instance."
                }

            # Simulate the edit to update current_content for next validation
            if replace_all:
                current_content = current_content.replace(old_string, new_string)
            else:
                current_content = current_content.replace(old_string, new_string, 1)

        # All validations passed, now apply all edits
        # Reset current_content to original
        if creating_new_file:
            final_content = ""
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    final_content = f.read()
            except UnicodeDecodeError:
                return {
                    "success": False,
                    "error": f"File is not a text file or has encoding issues: {file_path}",
                    "file_path": file_path,
                    "edits_processed": 0,
                    "total_edits": len(edits),
                    "content": f"ERROR: File is not a text file or has encoding issues: {file_path}"
                }

        # Apply all edits in sequence
        total_replacements = 0
        edit_details = []

        for i, edit in enumerate(edits):
            old_string = edit.get('old_string', '')
            new_string = edit.get('new_string', '')
            replace_all = edit.get('replace_all', False)

            # Handle new file creation
            if creating_new_file and i == 0 and old_string == '':
                final_content = new_string
                replacements_made = 1
            else:
                # Count occurrences before replacement
                occurrence_count = final_content.count(old_string)
                
                if replace_all:
                    final_content = final_content.replace(old_string, new_string)
                    replacements_made = occurrence_count
                else:
                    final_content = final_content.replace(old_string, new_string, 1)
                    replacements_made = 1

            total_replacements += replacements_made
            edit_details.append({
                "edit_number": i + 1,
                "replacements_made": replacements_made,
                "replace_all_used": replace_all,
                "old_string_preview": old_string[:50] + "..." if len(old_string) > 50 else old_string,
                "new_string_preview": new_string[:50] + "..." if len(new_string) > 50 else new_string
            })

        # Write the final content to file
        try:
            # Create directory if it doesn't exist (for new files)
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
        except PermissionError:
            return {
                "success": False,
                "error": f"Permission denied when writing to file: {file_path}",
                "file_path": file_path,
                "edits_processed": 0,
                "total_edits": len(edits),
                "content": f"ERROR: Permission denied when writing to file: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to write file: {str(e)}",
                "file_path": file_path,
                "edits_processed": 0,
                "total_edits": len(edits),
                "content": f"ERROR: Failed to write file: {str(e)}"
            }

        # Calculate statistics
        final_lines = len(final_content.splitlines())
        
        operation_type = "created" if creating_new_file else "edited"
        
        return {
            "success": True,
            "message": f"Successfully {operation_type} file with {len(edits)} edit operation(s), making {total_replacements} total replacement(s)",
            "file_path": file_path,
            "edits_processed": len(edits),
            "total_edits": len(edits),
            "total_replacements": total_replacements,
            "final_lines": final_lines,
            "file_size_bytes": len(final_content.encode('utf-8')),
            "operation_type": operation_type,
            "edit_details": edit_details,
            "content": f"Successfully {operation_type} file {file_path} with {len(edits)} edit operation(s), making {total_replacements} total replacement(s)"
        }

    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: {file_path}",
            "file_path": file_path,
            "edits_processed": 0,
            "total_edits": len(edits) if edits else 0,
            "content": f"ERROR: Permission denied: {file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "file_path": file_path,
            "edits_processed": 0,
            "total_edits": len(edits) if edits else 0,
            "content": f"ERROR: Unexpected error: {str(e)}"
        } 