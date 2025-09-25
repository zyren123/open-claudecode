#!/usr/bin/env python3

from tools.bashtool import bash_tool

def test_basic_commands():
    """Test basic bash commands"""
    print("=== Testing Basic Commands ===")
    
    # Test simple command
    result = bash_tool.invoke({"command": "echo 'Hello World'"})
    print(f"Echo test: {result['success']}")
    print(f"Output: {result['stdout'].strip()}")
    
    # Test ls command
    result = bash_tool.invoke({"command": "ls -la", "description": "List files in current directory"})
    print(f"\nLS test: {result['success']}")
    print(f"Files found: {len(result['stdout'].split('\n')) - 1} lines")
    
    # Test pwd
    result = bash_tool.invoke({"command": "pwd"})
    print(f"\nPWD test: {result['success']}")
    print(f"Current dir: {result['stdout'].strip()}")


def test_security():
    """Test security features"""
    print("\n=== Testing Security ===")
    
    # Test dangerous command blocking
    result = bash_tool.invoke({"command": "rm -rf README.md"})
    print(f"Dangerous command blocked: {not result['success']}")
    print(f"Error: {result['stderr']}")

def test_timeout():
    """Test timeout functionality"""
    print("\n=== Testing Timeout ===")
    
    # Test short timeout (should timeout)
    result = bash_tool.invoke({"command": "sleep 5", "timeout": 2000})  # 2 second timeout
    print(f"Timeout test: {not result['success']}")
    print(f"Error: {result['stderr']}")

if __name__ == "__main__":
    test_basic_commands()
    test_security()
    test_timeout()
    print("\n=== All tests completed ===") 