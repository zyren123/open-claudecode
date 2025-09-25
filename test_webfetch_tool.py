#!/usr/bin/env python3
"""
Test script for WebFetch tool
"""

import sys
import os

# Add the project root to the path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.webfetchtool import webfetch_tool

def test_basic_webfetch():
    """Test basic webfetch functionality"""
    print("Testing WebFetch tool...")
    print("=" * 50)
    
    # Test with a simple, reliable website
    url = "https://httpbin.org/get"
    prompt = "What is the structure of this JSON response? Summarize the key fields."
    
    print(f"URL: {url}")
    print(f"Prompt: {prompt}")
    print("-" * 30)
    
    try:
        result = webfetch_tool.invoke({"url": url, "prompt": prompt})
        
        if result["success"]:
            print("✅ WebFetch successful!")
            print(f"URL: {result['url']}")
            print(f"Content length: {result['content_length']} characters")
            print(f"Cached: {result['cached']}")
            print("\nAI Analysis Result:")
            print("-" * 30)
            print(result["result"])
        else:
            print("❌ WebFetch failed:")
            print(f"Error: {result['error']}")
            if result.get('is_redirect'):
                print(f"Redirect URL: {result.get('redirect_url')}")
                
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")

def test_cache_functionality():
    """Test cache functionality by making the same request twice"""
    print("\n" + "=" * 50)
    print("Testing cache functionality...")
    print("=" * 50)
    
    url = "https://httpbin.org/json"
    prompt = "Describe this JSON data"
    
    print("First request (should fetch from web):")
    print("-" * 30)
    
    try:
        result1 = webfetch_tool.invoke({"url": url, "prompt": prompt})
        if result1["success"]:
            print(f"✅ First request successful, cached: {result1['cached']}")
        else:
            print(f"❌ First request failed: {result1['error']}")
            return
        
        print("\nSecond request (should use cache):")
        print("-" * 30)
        
        result2 = webfetch_tool.invoke({"url": url, "prompt": prompt})
        if result2["success"]:
            print(f"✅ Second request successful, cached: {result2['cached']}")
            if result2['cached']:
                print("🎉 Cache is working correctly!")
            else:
                print("⚠️ Cache might not be working as expected")
        else:
            print(f"❌ Second request failed: {result2['error']}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")

def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n" + "=" * 50)
    print("Testing error handling...")
    print("=" * 50)
    
    # Test empty URL
    print("Testing empty URL:")
    result = webfetch_tool.invoke({"url": "", "prompt": "test prompt"})
    print(f"Empty URL result: {result['success']} - {result.get('error', 'No error')}")
    
    # Test empty prompt
    print("\nTesting empty prompt:")
    result = webfetch_tool.invoke({"url": "https://example.com", "prompt": ""})
    print(f"Empty prompt result: {result['success']} - {result.get('error', 'No error')}")
    
    # Test invalid URL
    print("\nTesting invalid URL:")
    result = webfetch_tool.invoke({"url": "not-a-url", "prompt": "test prompt"})
    print(f"Invalid URL result: {result['success']} - {result.get('error', 'No error')}")

if __name__ == "__main__":
    print("WebFetch Tool Test Suite")
    print("========================")
    
    try:
        test_basic_webfetch()
        test_cache_functionality()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("Note: Some tests may fail if:")
        print("- No internet connection")
        print("- LLM service is not configured")
        print("- Target websites are unavailable")
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}") 