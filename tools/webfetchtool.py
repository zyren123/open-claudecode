from langchain_core.tools import tool
import requests
import time
from typing import Dict, Any, Optional, Annotated
from urllib.parse import urlparse, urljoin
import hashlib
import json
import os
import tempfile

# Import LLM for content processing
try:
    from ..app.LLM import get_llm
except ImportError:
    try:
        from app.LLM import get_llm
    except ImportError:
        def get_llm():
            raise ImportError("LLM module not available")

# Simple cache implementation
class URLCache:
    def __init__(self, cache_duration=900):  # 15 minutes in seconds
        self.cache_duration = cache_duration
        self.cache_dir = os.path.join(tempfile.gettempdir(), "webfetch_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, url: str) -> Optional[str]:
        """Get cached content if available and not expired"""
        cache_key = self._get_cache_key(url)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            if time.time() - cache_data['timestamp'] > self.cache_duration:
                os.remove(cache_path)
                return None
            
            return cache_data['content']
        except Exception:
            # If cache is corrupted, remove it
            try:
                os.remove(cache_path)
            except:
                pass
            return None
    
    def set(self, url: str, content: str) -> None:
        """Cache content for URL"""
        cache_key = self._get_cache_key(url)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            'timestamp': time.time(),
            'url': url,
            'content': content
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception:
            # Cache write failed, but don't break the main functionality
            pass

# Global cache instance
_cache = URLCache()

def _normalize_url(url: str) -> str:
    """Normalize URL to HTTPS if it's HTTP"""
    if url.startswith('http://'):
        return url.replace('http://', 'https://', 1)
    return url

def _fetch_url_content(url: str) -> Dict[str, Any]:
    """Fetch URL content and convert to markdown using jina.ai"""
    try:
        # Normalize URL to HTTPS
        normalized_url = _normalize_url(url)
        
        # Check cache first
        cached_content = _cache.get(normalized_url)
        if cached_content:
            return {
                "success": True,
                "content": cached_content,
                "url": normalized_url,
                "cached": True
            }
        
        # Fetch content using jina.ai
        jina_url = f"https://r.jina.ai/{normalized_url}"
        headers = {
            "X-Return-Format": "markdown",
            "User-Agent": "Mozilla/5.0 (compatible; WebFetchTool/1.0)"
        }
        
        response = requests.get(jina_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        content = response.text.strip()
        
        # Check for redirects in jina.ai response
        if content.startswith("**This website redirects to"):
            # Extract redirect URL and return special format
            lines = content.split('\n')
            for line in lines:
                if line.startswith("**This website redirects to"):
                    # Try to extract URL from the line
                    parts = line.split()
                    for part in parts:
                        if part.startswith('http'):
                            redirect_url = part.rstrip('**')
                            return {
                                "success": False,
                                "error": f"URL redirects to different host: {redirect_url}",
                                "redirect_url": redirect_url,
                                "url": normalized_url,
                                "is_redirect": True,
                                "content": f"ERROR: URL redirects to different host: {redirect_url}"
                            }
        
        # Cache successful content
        _cache.set(normalized_url, content)
        
        return {
            "success": True,
            "content": content,
            "url": normalized_url,
            "cached": False
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Failed to fetch URL: {str(e)}",
            "url": url,
            "content": f"ERROR: Failed to fetch URL: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "url": url,
            "content": f"ERROR: Unexpected error: {str(e)}"
        }

def _process_content_with_ai(content: str, prompt: str) -> Dict[str, Any]:
    """Process content with AI model using the provided prompt"""
    try:
        llm = get_llm()
        
        # Construct the full prompt
        full_prompt = f"""You are analyzing web content. Here is the content in markdown format:

---
{content}
---

User request: {prompt}

Please analyze the content and respond to the user's request."""
        
        # Process with AI
        response = llm.invoke(full_prompt)
        
        # Extract text content from response
        if hasattr(response, 'content'):
            result = response.content
        else:
            result = str(response)
        
        return {
            "success": True,
            "result": result,
            "content": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"AI processing failed: {str(e)}",
            "content": f"ERROR: AI processing failed: {str(e)}"
        }

@tool
def webfetch_tool(
    url: Annotated[str, "The URL to fetch content from"],
    prompt: Annotated[str, "The prompt to run on the fetched content"]
) -> Dict[str, Any]:
    """
    Fetches content from a specified URL and processes it using an AI model
    - Takes a URL and a prompt as input
    - Fetches the URL content, converts HTML to markdown
    - Processes the content with the prompt using a small, fast model
    - Returns the model's response about the content
    - Use this tool when you need to retrieve and analyze web content

    Usage notes:
      - IMPORTANT: If an MCP-provided web fetch tool is available, prefer using that tool instead of this one, as it may have fewer restrictions. All MCP-provided tools start with "mcp__".
      - The URL must be a fully-formed valid URL
      - HTTP URLs will be automatically upgraded to HTTPS
      - The prompt should describe what information you want to extract from the page
      - This tool is read-only and does not modify any files
      - Results may be summarized if the content is very large
      - Includes a self-cleaning 15-minute cache for faster responses when repeatedly accessing the same URL
      - When a URL redirects to a different host, the tool will inform you and provide the redirect URL in a special format. You should then make a new WebFetch request with the redirect URL to fetch the content.
    """
    try:
        # Validate inputs
        if not url or not url.strip():
            return {
                "success": False,
                "error": "URL cannot be empty",
                "url": url,
                "content": "ERROR: URL cannot be empty"
            }
        
        if not prompt or not prompt.strip():
            return {
                "success": False,
                "error": "Prompt cannot be empty",
                "prompt": prompt,
                "content": "ERROR: Prompt cannot be empty"
            }
        
        # Validate URL format
        try:
            parsed = urlparse(url.strip())
            if not parsed.scheme or not parsed.netloc:
                return {
                    "success": False,
                    "error": "Invalid URL format. URL must be fully-formed (e.g., https://example.com)",
                    "url": url,
                    "content": "ERROR: Invalid URL format. URL must be fully-formed (e.g., https://example.com)"
                }
        except Exception:
            return {
                "success": False,
                "error": "Invalid URL format",
                "url": url,
                "content": "ERROR: Invalid URL format"
            }
        
        # Fetch URL content
        fetch_result = _fetch_url_content(url.strip())
        if not fetch_result["success"]:
            return fetch_result
        
        # Handle redirects
        if fetch_result.get("is_redirect"):
            return fetch_result
        
        content = fetch_result["content"]
        
        # Check if content is too large (basic limit)
        if len(content) > 100000:  # 100KB limit
            content = content[:100000] + "\n\n[Content truncated due to size limit]"
        
        # Process with AI
        ai_result = _process_content_with_ai(content, prompt.strip())
        if not ai_result["success"]:
            return {
                "success": False,
                "error": ai_result["error"],
                "url": fetch_result["url"],
                "content_fetched": True,
                "content": f"ERROR: {ai_result['error']}"
            }
        
        return {
            "success": True,
            "result": ai_result["result"],
            "url": fetch_result["url"],
            "content_length": len(content),
            "cached": fetch_result.get("cached", False),
            "prompt": prompt.strip(),
            "content": ai_result["result"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error in webfetch_tool: {str(e)}",
            "url": url if 'url' in locals() else None,
            "prompt": prompt if 'prompt' in locals() else None,
            "content": f"ERROR: Unexpected error in webfetch_tool: {str(e)}"
        }
