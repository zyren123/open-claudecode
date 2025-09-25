#!/usr/bin/env python3
"""
Test script for the glob_tool functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.globtool import glob_tool

def test_glob_tool():
    print("Testing glob_tool functionality...")
    
    # Test 1: Find all Python files in current directory
    print("\n1. Testing pattern '*.py':")
    result = glob_tool.invoke({"pattern": "*.py"})
    print(f"Success: {result['success']}")
    print(f"Count: {result['count']}")
    if result['success']:
        print("Found files:")
        for file in result['files'][:5]:  # Show first 5 files
            print(f"  - {file}")
        if result['count'] > 5:
            print(f"  ... and {result['count'] - 5} more files")
    else:
        print(f"Error: {result['error']}")
    
    # Test 2: Find all Python files recursively
    print("\n2. Testing pattern '**/*.py':")
    result = glob_tool.invoke({"pattern": "**/*.py"})
    print(f"Success: {result['success']}")
    print(f"Count: {result['count']}")
    if result['success']:
        print("Found files:")
        for file in result['files'][:5]:  # Show first 5 files
            print(f"  - {file}")
        if result['count'] > 5:
            print(f"  ... and {result['count'] - 5} more files")
    else:
        print(f"Error: {result['error']}")
    
    # Test 3: Test with specific directory path
    print("\n3. Testing with tools directory:")
    result = glob_tool.invoke({"pattern": "*.py", "path": "tools"})
    print(f"Success: {result['success']}")
    print(f"Count: {result['count']}")
    if result['success']:
        print("Found files:")
        for file in result['files']:
            print(f"  - {file}")
    else:
        print(f"Error: {result['error']}")
    
    # Test 4: Test with non-existent directory
    print("\n4. Testing with non-existent directory:")
    result = glob_tool.invoke({"pattern": "*.py", "path": "non_existent_dir"})
    print(f"Success: {result['success']}")
    if not result['success']:
        print(f"Expected error: {result['error']}")
    
    # Test 5: Test with pattern that matches no files
    print("\n5. Testing pattern that matches no files:")
    result = glob_tool.invoke({"pattern": "*.nonexistent"})
    print(f"Success: {result['success']}")
    print(f"Count: {result['count']}")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_glob_tool() 