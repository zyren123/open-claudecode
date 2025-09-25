#!/usr/bin/env python3
"""
Test script for the Edit tool to demonstrate its functionality.
"""

from tools.edittool import edit_tool, mark_file_as_read
from tools.readtool import read_tool
import tempfile
import os

def test_edit_tool():
    """Test the edit tool functionality."""
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_content = """Hello World!
This is a test file.
We will edit this content.
Hello World!
End of file."""
        f.write(test_content)
        temp_file = f.name
    
    print(f"Created temporary test file: {temp_file}")
    
    try:
        # Test 1: Try to edit without reading first (should fail)
        print("\n=== Test 1: Edit without reading first ===")
        result = edit_tool.invoke({"file_path": temp_file, "old_string": "Hello World!", "new_string": "Goodbye World!"})
        print(f"Success: {result['success']}")
        print(f"Error: {result.get('error', 'None')}")
        
        # Test 2: Read the file first
        print("\n=== Test 2: Read the file ===")
        read_result = read_tool.invoke({"file_path": temp_file})
        print(f"Read success: {read_result['success']}")
        print("File content:")
        print(read_result['content'][:200] + "..." if len(read_result['content']) > 200 else read_result['content'])
        
        # Test 3: Edit with non-unique string (should fail)
        print("\n=== Test 3: Edit with non-unique string ===")
        result = edit_tool.invoke({"file_path": temp_file, "old_string": "Hello World!", "new_string": "Goodbye World!"})
        print(f"Success: {result['success']}")
        print(f"Error: {result.get('error', 'None')}")
        print(f"Occurrences: {result.get('occurrences', 'N/A')}")
        
        # Test 4: Edit with unique string (should succeed)
        print("\n=== Test 4: Edit with unique string ===")
        result = edit_tool.invoke({"file_path": temp_file, "old_string": "This is a test file.", "new_string": "This is a modified test file."})
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'None')}")
        print(f"Replacements made: {result.get('replacements_made', 'N/A')}")
        
        # Test 5: Read file again to see changes
        print("\n=== Test 5: Read file after edit ===")
        read_result = read_tool.invoke({"file_path": temp_file})
        print("Updated file content:")
        print(read_result['content'][:200] + "..." if len(read_result['content']) > 200 else read_result['content'])
        
        # Test 6: Use replace_all for multiple occurrences
        print("\n=== Test 6: Replace all occurrences ===")
        result = edit_tool.invoke({"file_path": temp_file, "old_string": "Hello World!", "new_string": "Goodbye World!", "replace_all": True})
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'None')}")
        print(f"Replacements made: {result.get('replacements_made', 'N/A')}")
        
        # Test 7: Final read to see all changes
        print("\n=== Test 7: Final file content ===")
        read_result = read_tool.invoke({"file_path": temp_file})
        print("Final file content:")
        print(read_result['content'])
        
        # Test 8: Test error cases
        print("\n=== Test 8: Error cases ===")
        
        # Non-existent file
        result = edit_tool.invoke({"file_path": "/nonexistent/file.txt", "old_string": "old", "new_string": "new"})
        print(f"Non-existent file - Success: {result['success']}, Error: {result.get('error', 'None')}")
        
        # Same old and new string
        result = edit_tool.invoke({"file_path": temp_file, "old_string": "same", "new_string": "same"})
        print(f"Same strings - Success: {result['success']}, Error: {result.get('error', 'None')}")
        
        # String not found
        result = edit_tool.invoke({"file_path": temp_file, "old_string": "not found", "new_string": "replacement"})
        print(f"String not found - Success: {result['success']}, Error: {result.get('error', 'None')}")
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file)
            print(f"\nCleaned up temporary file: {temp_file}")
        except Exception as e:
            print(f"Error cleaning up: {e}")

if __name__ == "__main__":
    test_edit_tool() 