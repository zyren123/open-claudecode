#!/usr/bin/env python3
"""
Test script for the read_tool LangChain tool.
Tests various scenarios including text files, non-existent files, and error cases.
"""

import os
import tempfile
from tools.readtool import read_tool


def test_read_tool():
    """Test the read_tool function with various scenarios."""
    
    print("🧪 Testing read_tool function...\n")
    
    # Test 1: Create a temporary text file
    print("📝 Test 1: Reading a normal text file")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        test_content = "Line 1: Hello World\nLine 2: This is a test\nLine 3: Testing read tool\nLine 4: Final line"
        temp_file.write(test_content)
        temp_file_path = temp_file.name
    
    try:
        result = read_tool.invoke({"file_path": temp_file_path})
        print(f"✅ Success: {result['success']}")
        print(f"📊 Lines read: {result['lines_read']}")
        print(f"📄 Content:\n{result['content']}")
        print(f"🔍 File size: {result['file_size']} bytes")
        print()
    finally:
        os.unlink(temp_file_path)
    
    # Test 2: Test with offset and limit
    print("📝 Test 2: Reading with offset and limit")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        lines = [f"Line {i}: Content line {i}" for i in range(1, 11)]
        temp_file.write('\n'.join(lines))
        temp_file_path = temp_file.name
    
    try:
        result = read_tool.invoke({"file_path": temp_file_path, "offset": 3, "limit": 3})
        print(f"✅ Success: {result['success']}")
        print(f"📊 Lines read: {result['lines_read']}")
        print(f"🔢 Start line: {result['start_line']}")
        print(f"📄 Content:\n{result['content']}")
        print()
    finally:
        os.unlink(temp_file_path)
    
    # Test 3: Test empty file
    print("📝 Test 3: Reading an empty file")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_file_path = temp_file.name
    
    try:
        result = read_tool.invoke({"file_path": temp_file_path})
        print(f"✅ Success: {result['success']}")
        print(f"📄 Content: {result['content']}")
        print(f"📊 Lines read: {result['lines_read']}")
        print()
    finally:
        os.unlink(temp_file_path)
    
    # Test 4: Test non-existent file
    print("📝 Test 4: Reading a non-existent file")
    result = read_tool.invoke({"file_path": "/nonexistent/path/file.txt"})
    print(f"❌ Success: {result['success']}")
    print(f"🚫 Error: {result['error']}")
    print()
    
    # Test 5: Test relative path (should fail)
    print("📝 Test 5: Testing relative path (should fail)")
    result = read_tool.invoke({"file_path": "relative/path/file.txt"})
    print(f"❌ Success: {result['success']}")
    print(f"🚫 Error: {result['error']}")
    print()
    
    # Test 6: Test reading directory (should fail)
    print("📝 Test 6: Testing directory path (should fail)")
    result = read_tool.invoke({"file_path": "/tmp"})
    print(f"❌ Success: {result['success']}")
    print(f"🚫 Error: {result['error']}")
    print()
    
    # Test 7: Test long lines (truncation)
    print("📝 Test 7: Testing line truncation")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        long_line = "A" * 2500  # Line longer than 2000 characters
        temp_file.write(f"Short line\n{long_line}\nAnother short line")
        temp_file_path = temp_file.name
    
    try:
        result = read_tool.invoke({"file_path": temp_file_path})
        print(f"✅ Success: {result['success']}")
        print(f"📊 Lines read: {result['lines_read']}")
        lines = result['content'].split('\n')
        for i, line in enumerate(lines):
            if "TRUNCATED" in line:
                print(f"✂️  Line {i+1} was truncated (length: {len(line)})")
            else:
                print(f"📄 Line {i+1}: {line}")
        print()
    finally:
        os.unlink(temp_file_path)
    
    # Test 8: Test reading the tool itself
    print("📝 Test 8: Reading the readtool.py file (first 10 lines)")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    readtool_path = os.path.join(current_dir, "tools", "readtool.py")
    
    if os.path.exists(readtool_path):
        result = read_tool.invoke({"file_path": readtool_path, "limit": 10})
        print(f"✅ Success: {result['success']}")
        print(f"📊 Lines read: {result['lines_read']}")
        print(f"📄 First 10 lines of readtool.py:")
        print(result['content'])
        print()
    else:
        print(f"⚠️  Could not find readtool.py at {readtool_path}")
        print()
    
    print("🎉 All tests completed!")


if __name__ == "__main__":
    test_read_tool() 