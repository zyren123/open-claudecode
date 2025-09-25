#!/usr/bin/env python3
"""
Test script for the write_tool LangChain tool.
Tests various scenarios including creating new files, overwriting existing files, and error cases.
"""

import os
import tempfile
from tools.writetool import write_tool
from tools.readtool import read_tool


def test_write_tool():
    """Test the write_tool function with various scenarios."""
    
    print("🧪 Testing write_tool function...\n")
    
    # Test 1: Create a new file
    print("📝 Test 1: Creating a new file")
    with tempfile.TemporaryDirectory() as temp_dir:
        new_file_path = os.path.join(temp_dir, "new_file.txt")
        test_content = "Hello World!\nThis is a new file.\nCreated by write_tool."
        
        result = write_tool.invoke({"file_path": new_file_path, "content": test_content})
        print(f"✅ Success: {result['success']}")
        print(f"📄 Operation: {result['operation']}")
        print(f"📊 Content lines: {result['content_lines']}")
        print(f"🔍 File size: {result['new_size_bytes']} bytes")
        print(f"📂 File path: {result['file_path']}")
        print()
    
    # Test 2: Overwrite existing file (should fail without reading first)
    print("📝 Test 2: Attempting to overwrite without reading first (should fail)")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_file.write("Original content")
        temp_file_path = temp_file.name
    
    try:
        result = write_tool.invoke({"file_path": temp_file_path, "content": "New content"})
        print(f"❌ Success: {result['success']}")
        print(f"🚫 Error: {result['error']}")
        print()
    finally:
        os.unlink(temp_file_path)
    
    # Test 3: Read file first, then overwrite (should succeed)
    print("📝 Test 3: Reading file first, then overwriting (should succeed)")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        original_content = "Original content\nLine 2\nLine 3"
        temp_file.write(original_content)
        temp_file_path = temp_file.name
    
    try:
        # First read the file
        read_result = read_tool.invoke({"file_path": temp_file_path})
        print(f"📖 Read operation success: {read_result['success']}")
        print(f"📄 Original content:\n{read_result['content']}")
        print()
        
        # Now overwrite it
        new_content = "Overwritten content!\nThis file has been updated.\nNew line 3\nNew line 4"
        write_result = write_tool.invoke({"file_path": temp_file_path, "content": new_content})
        print(f"✅ Write success: {write_result['success']}")
        print(f"📄 Operation: {write_result['operation']}")
        print(f"📊 Original size: {write_result['original_size_bytes']} bytes")
        print(f"📊 New size: {write_result['new_size_bytes']} bytes")
        print(f"📊 Content lines: {write_result['content_lines']}")
        print()
        
        # Verify the content was written
        verify_result = read_tool.invoke({"file_path": temp_file_path})
        print(f"🔍 Verification - New content:\n{verify_result['content']}")
        print()
    finally:
        os.unlink(temp_file_path)
    
    # Test 4: Test relative path (should fail)
    print("📝 Test 4: Testing relative path (should fail)")
    result = write_tool.invoke({"file_path": "relative/path/file.txt", "content": "content"})
    print(f"❌ Success: {result['success']}")
    print(f"🚫 Error: {result['error']}")
    print()
    
    # Test 5: Test writing to directory path (should fail)
    print("📝 Test 5: Testing directory path (should fail)")
    with tempfile.TemporaryDirectory() as temp_dir:
        result = write_tool.invoke({"file_path": temp_dir, "content": "content"})
        print(f"❌ Success: {result['success']}")
        print(f"🚫 Error: {result['error']}")
        print()
    
    # Test 6: Test creating file in new directory
    print("📝 Test 6: Creating file in new directory")
    with tempfile.TemporaryDirectory() as temp_dir:
        new_dir_path = os.path.join(temp_dir, "new_directory", "nested")
        new_file_path = os.path.join(new_dir_path, "file.txt")
        test_content = "File in new directory structure"
        
        result = write_tool.invoke({"file_path": new_file_path, "content": test_content})
        print(f"✅ Success: {result['success']}")
        print(f"📄 Operation: {result['operation']}")
        print(f"📂 Created directories and file: {result['file_path']}")
        print(f"📊 Content chars: {result['content_chars']}")
        print()
    
    # Test 7: Test empty content
    print("📝 Test 7: Writing empty content")
    with tempfile.TemporaryDirectory() as temp_dir:
        empty_file_path = os.path.join(temp_dir, "empty_file.txt")
        
        result = write_tool.invoke({"file_path": empty_file_path, "content": ""})
        print(f"✅ Success: {result['success']}")
        print(f"📄 Operation: {result['operation']}")
        print(f"📊 Content lines: {result['content_lines']}")
        print(f"📊 Content chars: {result['content_chars']}")
        print()
    
    # Test 8: Test large content
    print("📝 Test 8: Writing large content")
    with tempfile.TemporaryDirectory() as temp_dir:
        large_file_path = os.path.join(temp_dir, "large_file.txt")
        large_content = "\n".join([f"Line {i}: This is a test line with some content." for i in range(1, 1001)])
        
        result = write_tool.invoke({"file_path": large_file_path, "content": large_content})
        print(f"✅ Success: {result['success']}")
        print(f"📄 Operation: {result['operation']}")
        print(f"📊 Content lines: {result['content_lines']}")
        print(f"📊 Content chars: {result['content_chars']}")
        print(f"🔍 File size: {result['new_size_bytes']} bytes")
        print()
    
    # Test 9: Test overwriting with different content length
    print("📝 Test 9: Overwriting with different content length")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        original_content = "Short content"
        temp_file.write(original_content)
        temp_file_path = temp_file.name
    
    try:
        # Read first
        read_tool.invoke({"file_path": temp_file_path})
        
        # Overwrite with much longer content
        new_content = "This is much longer content\n" * 50
        result = write_tool.invoke({"file_path": temp_file_path, "content": new_content})
        print(f"✅ Success: {result['success']}")
        print(f"📄 Operation: {result['operation']}")
        print(f"📊 Original size: {result['original_size_bytes']} bytes")
        print(f"📊 New size: {result['new_size_bytes']} bytes")
        print(f"📈 Size change: {result['new_size_bytes'] - result['original_size_bytes']} bytes")
        print()
    finally:
        os.unlink(temp_file_path)
    
    print("🎉 All tests completed!")


if __name__ == "__main__":
    test_write_tool() 