#!/usr/bin/env python3

"""Test script for grep_tool functionality"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.greptool import grep_tool

def test_files_with_matches():
    """Test finding files containing 'def' keyword"""
    print("=== Test: Files with matches mode ===")
    result = grep_tool.invoke({"pattern": "def ", "glob": "*.py", "output_mode": "files_with_matches"})
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Using: {result.get('tool_used', 'unknown')}")
        print(f"Found {result['count']} files:")
        for file in result.get('files', [])[:5]:  # Show first 5
            print(f"  {file}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    print()

def test_content_mode():
    """Test showing actual content with line numbers"""
    print("=== Test: Content mode with line numbers ===")
    result = grep_tool.invoke({"pattern": "@tool", "glob": "*.py", "output_mode": "content", "n": True, "head_limit": 10})
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Using: {result.get('tool_used', 'unknown')}")
        content = result.get('content', '')
        if content:
            print("Content found:")
            print(content)
        else:
            print("No matches found")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    print()

def test_count_mode():
    """Test counting matches per file"""
    print("=== Test: Count mode ===")
    result = grep_tool.invoke({"pattern": "import", "glob": "*.py", "output_mode": "count"})

    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Using: {result.get('tool_used', 'unknown')}")
        print(f"Total matches: {result['total_matches']} in {result['total_files']} files")
        for file, count in list(result.get('file_counts', {}).items())[:3]:
            print(f"  {file}: {count} matches")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    print()

def test_case_insensitive():
    """Test case insensitive search"""
    print("=== Test: Case insensitive search ===")
    result = grep_tool.invoke({"pattern": "TOOL", "glob": "*.py", "output_mode": "files_with_matches", "i": True})
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Using: {result.get('tool_used', 'unknown')}")
        print(f"Found {result['count']} files with case-insensitive match")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    print()

def test_invalid_path():
    """Test handling of invalid path"""
    print("=== Test: Invalid path handling ===")
    result = grep_tool.invoke({"pattern": "test", "path": "/non/existent/path"})
    print(f"Success: {result['success']}")
    if not result['success']:
        print(f"Error (expected): {result.get('error', 'Unknown error')}")
    print()

if __name__ == "__main__":
    print("Testing grep_tool implementation\n")
    
    # Run all tests
    test_files_with_matches()
    test_content_mode()
    test_count_mode()
    test_case_insensitive()
    test_invalid_path()
    
    print("Testing completed!") 