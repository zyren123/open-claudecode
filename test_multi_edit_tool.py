#!/usr/bin/env python3
"""
Test script for the MultiEdit tool to demonstrate its functionality.
"""

from tools.multiedittool import multi_edit_tool
from tools.readtool import read_tool
import tempfile
import os

def test_multi_edit_tool():
    """Test the multi edit tool functionality."""
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_content = """Hello World!
This is a test file.
We will edit this content.
Hello World!
var oldName = "test";
console.log("Hello World!");
End of file."""
        f.write(test_content)
        temp_file = f.name
    
    print(f"Created temporary test file: {temp_file}")
    
    try:
        # Test 1: Try to edit without reading first (should fail)
        print("\n=== Test 1: MultiEdit without reading first ===")
        result = multi_edit_tool.invoke({
            "file_path": temp_file,
            "edits": [
                {"old_string": "Hello World!", "new_string": "Goodbye World!"}
            ]
        })
        print(f"Success: {result['success']}")
        print(f"Error: {result.get('error', 'None')}")
        
        # Test 2: Read the file first
        print("\n=== Test 2: Read the file ===")
        read_result = read_tool.invoke({"file_path": temp_file})
        print(f"Read success: {read_result['success']}")
        print("File content:")
        print(read_result['content'])
        
        # Test 3: Multiple edits with atomic failure (should fail - old_string appears multiple times)
        print("\n=== Test 3: Multiple edits with atomic failure ===")
        result = multi_edit_tool.invoke({
            "file_path": temp_file,
            "edits": [
                {"old_string": "Hello World!", "new_string": "Goodbye World!"},  # This will fail - multiple occurrences
                {"old_string": "test file", "new_string": "modified file"}
            ]
        })
        print(f"Success: {result['success']}")
        print(f"Error: {result.get('error', 'None')}")
        print(f"Failed edit: {result.get('failed_edit', 'N/A')}")
        
        # Test 4: Successful multiple edits with unique strings
        print("\n=== Test 4: Successful multiple edits ===")
        result = multi_edit_tool.invoke({
            "file_path": temp_file,
            "edits": [
                {"old_string": "This is a test file.", "new_string": "This is a modified test file."},
                {"old_string": "We will edit this content.", "new_string": "We have edited this content successfully."},
                {"old_string": "var oldName", "new_string": "var newName"}
            ]
        })
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'None')}")
        print(f"Edits processed: {result.get('edits_processed', 'N/A')}")
        print(f"Total replacements: {result.get('total_replacements', 'N/A')}")
        
        # Test 5: Read file to see changes
        print("\n=== Test 5: Read file after multiple edits ===")
        read_result = read_tool.invoke({"file_path": temp_file})
        print("Updated file content:")
        print(read_result['content'])
        
        # Test 6: Use replace_all for multiple occurrences
        print("\n=== Test 6: Replace all occurrences ===")
        result = multi_edit_tool.invoke({
            "file_path": temp_file,
            "edits": [
                {"old_string": "Hello World!", "new_string": "Goodbye World!", "replace_all": True}
            ]
        })
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'None')}")
        print(f"Edit details: {result.get('edit_details', [])}")
        
        # Test 7: Read final content
        print("\n=== Test 7: Final file content ===")
        read_result = read_tool.invoke({"file_path": temp_file})
        print("Final file content:")
        print(read_result['content'])
        
        # Test 8: Create a new file using MultiEdit
        new_file_path = temp_file.replace(".txt", "_new.txt")
        print(f"\n=== Test 8: Create new file at {new_file_path} ===")
        result = multi_edit_tool.invoke({
            "file_path": new_file_path,
            "edits": [
                {"old_string": "", "new_string": "# New Python File\nprint('Hello from new file')\n"},
                # {"old_string": "Hello from new file", "new_string": "Hello from newly created file"}
            ]
        })
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'None')}")
        print(f"Error: {result.get('error', 'None')}")
        print(f"Operation type: {result.get('operation_type', 'N/A')}")
        
        # Test 9: Read the new file
        print("\n=== Test 9: Read newly created file ===")
        read_result = read_tool.invoke({"file_path": new_file_path})
        print("New file content:")
        print(read_result['content'])
        
        # Test 10: Error cases
        print("\n=== Test 10: Error cases ===")
        
        # Empty edits array (should be caught by schema, but let's test)
        result = multi_edit_tool.invoke({
            "file_path": temp_file,
            "edits": []
        })
        print(f"Empty edits - Success: {result['success']}, Error: {result.get('error', 'None')}")
        
        # Non-existent file
        result = multi_edit_tool.invoke({
            "file_path": "/nonexistent/file.txt",
            "edits": [{"old_string": "old", "new_string": "new"}]
        })
        print(f"Non-existent file - Success: {result['success']}, Error: {result.get('error', 'None')}")
        
        # Same old and new string
        result = multi_edit_tool.invoke({
            "file_path": temp_file,
            "edits": [{"old_string": "same", "new_string": "same"}]
        })
        print(f"Same strings - Success: {result['success']}, Error: {result.get('error', 'None')}")
        
        # Clean up new file
        try:
            os.unlink(new_file_path)
            print(f"Cleaned up new file: {new_file_path}")
        except:
            pass
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file)
            print(f"\nCleaned up temporary file: {temp_file}")
        except Exception as e:
            print(f"Error cleaning up: {e}")

if __name__ == "__main__":
    test_multi_edit_tool() 