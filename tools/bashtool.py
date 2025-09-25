from langchain_core.tools import tool
import subprocess
import os
from typing import Dict, Any, Optional, Annotated


@tool
def bash_tool(
    command: Annotated[str, "The command to execute"], 
    timeout: Annotated[Optional[int], "Optional timeout in milliseconds (max 600000)"] = 120000, 
    description: Annotated[Optional[str], "Clear, concise description of what this command does in 5-10 words. Examples:\nInput: ls\nOutput: Lists files in current directory\n\nInput: git status\nOutput: Shows working tree status\n\nInput: npm install\nOutput: Installs package dependencies\n\nInput: mkdir foo\nOutput: Creates directory 'foo'"] = None
) -> Dict[str, Any]:
    """Executes bash commands in a persistent shell session with timeout and security measures.

    BASIC USAGE:
    - Command argument is required
    - Optional timeout: max 600000ms (10 min), default 120000ms (2 min)
    - Description helps document what the command does (5-10 words)
    - Output truncated at 30000 characters

    EXECUTION RULES:
    - Quote paths with spaces: cd "/path with spaces/file.txt"
    - Use absolute paths when possible to avoid cd usage
    - Chain commands with ';' or '&&', NOT newlines
    - NEVER use: find, grep, cat, head, tail, ls (use dedicated tools instead)
    - For grep needs: use ripgrep (rg) which is pre-installed

    DIRECTORY VERIFICATION:
    Before creating files/directories, verify parent directory exists using LS tool.
    Example: Before "mkdir foo/bar", check that "foo" exists.

    ════════════════════════════════════════════════════════════════════════════════
    GIT COMMIT WORKFLOW:
    
    When user requests git commit:
    
    1. GATHER INFO (run in parallel):
       - git status (untracked files)
       - git diff (staged/unstaged changes)
       - git log (recent commit message style)
    
    2. ANALYZE & DRAFT:
       - Summarize change nature (feature/fix/refactor/etc.)
       - Check for sensitive info
       - Draft concise commit message (focus on "why")
    
    3. EXECUTE (run in parallel):
       - Add relevant untracked files
       - Commit with HEREDOC format (see example below)
       - Verify with git status
    
    4. RETRY ONCE if pre-commit hooks modify files

    COMMIT MESSAGE FORMAT:
    git commit -m "$(cat <<'EOF'
    Your commit message here.

    🤖 Generated with [Claude Code](https://claude.ai/code)

    Co-Authored-By: Claude <noreply@anthropic.com>
    EOF
    )"

    ════════════════════════════════════════════════════════════════════════════════
    PULL REQUEST WORKFLOW:
    
    When user requests PR creation:
    
    1. ANALYZE BRANCH (run in parallel):
       - git status (untracked files)
       - git diff (staged/unstaged changes)
       - Check remote tracking status
       - git log + git diff [base]...HEAD (full branch history)
    
    2. DRAFT PR SUMMARY:
       Review ALL commits in branch (not just latest)
    
    3. CREATE PR (run in parallel):
       - Create/push branch if needed
       - Use gh pr create with HEREDOC body format

    PR BODY FORMAT:
    gh pr create --title "title" --body "$(cat <<'EOF'
    ## Summary
    <1-3 bullet points>

    ## Test plan
    [Testing checklist]

    🤖 Generated with [Claude Code](https://claude.ai/code)
    EOF
    )"

    ════════════════════════════════════════════════════════════════════════════════
    RESTRICTIONS:
    - NEVER update git config
    - NEVER use interactive git flags (-i)
    - NEVER push unless explicitly requested
    - NEVER use TodoWrite or Task tools for git operations
    - Use gh command for all GitHub operations

    OTHER GITHUB OPERATIONS:
    - View PR comments: gh api repos/owner/repo/pulls/123/comments
    """
    # Validate timeout
    if timeout is None:
        timeout = 120000
    if timeout > 600000:
        timeout = 600000
    
    # Convert milliseconds to seconds for subprocess
    timeout_seconds = timeout / 1000.0
    print(f"Executing command: {command}")
    print(f"Description: {description}") if description else print("No description provided")
    # Basic security: strip dangerous patterns (basic protection)
    dangerous_patterns = ['rm -rf ', 'mkfs', 'dd if=/dev/zero', ':(){ :|:& };:']
    for pattern in dangerous_patterns:
        if pattern in command:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command contains potentially dangerous pattern: {pattern}",
                "return_code": -1,
                "command": command,
                "content": f"ERROR: Command contains potentially dangerous pattern: {pattern}"
            }
    
    try:
        # Execute command
        # Using shell=True for bash compatibility, but this requires trust in input
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=os.getcwd()
        )
        
        # Truncate output if too long (30000 chars limit as per spec)
        stdout = result.stdout
        stderr = result.stderr
        
        if len(stdout) > 30000:
            stdout = stdout[:30000] + "\n... (output truncated)"
        if len(stderr) > 30000:
            stderr = stderr[:30000] + "\n... (error output truncated)"
        
        return {
            "success": result.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": result.returncode,
            "command": command,
            "content": stdout if result.returncode == 0 else f"ERROR (exit code {result.returncode}): {stderr if stderr else 'Command failed'}"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command timed out after {timeout_seconds} seconds",
            "return_code": -1,
            "command": command,
            "content": f"ERROR: Command timed out after {timeout_seconds} seconds"
        }
    except subprocess.SubprocessError as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Subprocess error: {str(e)}",
            "return_code": -1,
            "command": command,
            "content": f"ERROR: Subprocess error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Unexpected error: {str(e)}",
            "return_code": -1,
            "command": command,
            "content": f"ERROR: Unexpected error: {str(e)}"
        }


