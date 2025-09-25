from langchain_core.tools import tool
from typing import Dict, Any, Annotated
import asyncio
import concurrent.futures


@tool
def task_tool(
    description: Annotated[str, "A short (3-5 word) description of the task"],
    prompt: Annotated[str, "The task for the agent to perform"],
    subagent_type: Annotated[str, "The type of specialized agent to use for this task"]
) -> Dict[str, Any]:
    """
    Launch a new agent to handle complex, multi-step tasks autonomously.

    Available agent types and the tools they have access to:
    - general-purpose: General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you. (Tools: *)

    When using the Task tool, you must specify a subagent_type parameter to select which agent type to use.

    When to use the Agent tool:
    - When you are instructed to execute custom slash commands. Use the Agent tool with the slash command invocation as the entire prompt. The slash command can take arguments. For example: Task(description="Check the file", prompt="/check-file path/to/file.py")

    When NOT to use the Agent tool:
    - If you want to read a specific file path, use the Read or Glob tool instead of the Agent tool, to find the match more quickly
    - If you are searching for a specific class definition like "class Foo", use the Glob tool instead, to find the match more quickly
    - If you are searching for code within a specific file or set of 2-3 files, use the Read tool instead of the Agent tool, to find the match more quickly
    - Other tasks that are not related to the agent descriptions above


    Usage notes:
    1. Launch multiple agents concurrently whenever possible, to maximize performance; to do that, use a single message with multiple tool uses
    2. When the agent is done, it will return a single message back to you. The result returned by the agent is not visible to the user. To show the user the result, you should send a text message back to the user with a concise summary of the result.
    3. Each agent invocation is stateless. You will not be able to send additional messages to the agent, nor will the agent be able to communicate with you outside of its final report. Therefore, your prompt should contain a highly detailed task description for the agent to perform autonomously and you should specify exactly what information the agent should return back to you in its final and only message to you.
    4. The agent's outputs should generally be trusted
    5. Clearly tell the agent whether you expect it to write code or just to do research (search, file reads, web fetches, etc.), since it is not aware of the user's intent
    6. If the agent description mentions that it should be used proactively, then you should try your best to use it without the user having to ask for it first. Use your judgement.

    Example usage:

    <example_agent_descriptions>
    "code-reviewer": use this agent after you are done writing a signficant piece of code
    "greeting-responder": use this agent when to respond to user greetings with a friendly joke
    </example_agent_description>

    <example>
    user: "Please write a function that checks if a number is prime"
    assistant: Sure let me write a function that checks if a number is prime
    assistant: First let me use the Write tool to write a function that checks if a number is prime
    assistant: I'm going to use the Write tool to write the following code:
    <code>
    function isPrime(n) {
      if (n <= 1) return false
      for (let i = 2; i * i <= n; i++) {
        if (n % i === 0) return false
      }
      return true
    }
    </code>
    <commentary>
    Since a signficant piece of code was written and the task was completed, now use the code-reviewer agent to review the code
    </commentary>
    assistant: Now let me use the code-reviewer agent to review the code
    assistant: Uses the Task tool to launch the with the code-reviewer agent
    </example>

    <example>
    user: "Hello"
    <commentary>
    Since the user is greeting, use the greeting-responder agent to respond with a friendly joke
    </commentary>
    assistant: "I'm going to use the Task tool to launch the with the greeting-responder agent"
    </example>
    """
    try:
        # Lazy import to avoid circular dependency
        from app.Agent import ReactAgent
        
        # Create a new ReactAgent instance as sub-agent
        sub_agent = ReactAgent(is_main=False)
        
        # Execute the react loop in a separate thread to avoid event loop conflicts
        async def execute_task():
            return await sub_agent.reason_and_act(prompt)
        
        # Run async code in a separate thread
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, execute_task())
            result = future.result()
        
        return {
            "content": f"Task '{description}' completed successfully.\n\nAgent Type: {subagent_type}\n\nResult:\n{result}",
            "description": description,
            "subagent_type": subagent_type,
            "success": True
        }
        
    except Exception as e:
        return {
            "content": f"Task '{description}' failed with error: {str(e)}",
            "description": description,
            "subagent_type": subagent_type,
            "success": False,
            "error": str(e)
        }


