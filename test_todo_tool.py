#!/usr/bin/env python3
"""
Test script for todo_write_tool functionality
"""

from tools.todowritetool import todo_write_tool
from tools.tasktool import task_tool
import json

def test_todo_write_tool():
    """Test the todo_write_tool with various scenarios"""
    
    print("=== Testing TodoWrite Tool ===\n")
    
    # Test 1: Valid todo list
    print("Test 1: Valid todo list")
    test_todos = [
        {
            "content": "Implement user authentication",
            "status": "pending", 
            "priority": "high",
            "id": "task1"
        },
        {
            "content": "Add dark mode toggle",
            "status": "in_progress",
            "priority": "medium", 
            "id": "task2"
        },
        {
            "content": "Write unit tests",
            "status": "pending",
            "priority": "low",
            "id": "task3"
        }
    ]
    
    result = todo_write_tool.invoke({"todos": test_todos})
    print(f"Result: {json.dumps(result, indent=2)}")
    print()
    
    # Test 2: Invalid status
    print("Test 2: Invalid status")
    invalid_todos = [
        {
            "content": "Test task",
            "status": "invalid_status",
            "priority": "high", 
            "id": "task4"
        }
    ]
    
    result = todo_write_tool.invoke({"todos": invalid_todos})
    print(f"Result: {json.dumps(result, indent=2)}")
    print()
    
    # Test 3: Multiple in_progress tasks (should fail)
    print("Test 3: Multiple in_progress tasks")
    multiple_in_progress = [
        {
            "content": "Task 1",
            "status": "in_progress",
            "priority": "high",
            "id": "task5"
        },
        {
            "content": "Task 2", 
            "status": "in_progress",
            "priority": "medium",
            "id": "task6"
        }
    ]
    
    result = todo_write_tool.invoke({"todos": multiple_in_progress})
    print(f"Result: {json.dumps(result, indent=2)}")
    print()
    
    # Test 4: Auto-generate ID
    print("Test 4: Auto-generate ID")
    no_id_todos = [
        {
            "content": "Task without ID",
            "status": "pending",
            "priority": "medium",
            "id": ""
        }
    ]
    
    result = todo_write_tool.invoke({"todos": no_id_todos})
    print(f"Result: {json.dumps(result, indent=2)}")
    print()


if __name__ == "__main__":
    test_todo_write_tool()
    print("All tests completed!") 