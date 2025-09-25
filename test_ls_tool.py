#!/usr/bin/env python3
"""
Test script for the ls_tool
"""

from tools.lstool import ls_tool
import os

def test_ls_tool():
    print("Testing ls_tool...")
    
    # Test 1: List current directory (absolute path)
    current_dir = os.path.abspath(".")
    print(f"\n1. Testing with current directory: {current_dir}")
    result = ls_tool.invoke({"path": current_dir})
    print(f"Success: {result['success']}")
    print(f"Count: {result['count']}")
    print(f"Summary: {result['summary']}")
    
    # Test 2: Test with ignore patterns
    print(f"\n2. Testing with ignore patterns (*.py)")
    result_filtered = ls_tool.invoke({"path": current_dir, "ignore": ["*.py"]})
    print(f"Success: {result_filtered['success']}")
    print(f"Count: {result_filtered['count']}")
    print(f"Files without .py: {[e['name'] for e in result_filtered['entries'][:5]]}")
    
    # Test 3: Test error case - relative path
    print(f"\n3. Testing error case (relative path)")
    result_error = ls_tool.invoke({"path": "."})
    print(f"Success: {result_error['success']}")
    print(f"Error: {result_error['error']}")
    
    # Test 4: Test error case - non-existent path
    print(f"\n4. Testing error case (non-existent path)")
    result_not_found = ls_tool.invoke({"path": "/nonexistent/path"})
    print(f"Success: {result_not_found['success']}")
    print(f"Error: {result_not_found['error']}")

if __name__ == "__main__":
    test_ls_tool() 