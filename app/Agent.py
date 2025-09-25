from app.LLM import get_llm_with_tools
from tools import bash_tool, edit_tool, grep_tool, glob_tool, ls_tool, multi_edit_tool, read_tool, write_tool, webfetch_tool,task_tool,todo_write_tool,websearch_tool
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage
from prompt import sub_agent_system_prompt,main_agent_system_prompt,get_character_info_prompt,system_reminder,todo_list_reminder,get_todo_list_changed_reminder

# ANSI color constants
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'

class ReactAgent:
    def __init__(self,is_main: bool):
        self.mainagent=get_llm_with_tools([bash_tool, edit_tool, grep_tool, glob_tool, ls_tool, multi_edit_tool, read_tool, write_tool,webfetch_tool,task_tool,todo_write_tool])
        self.subagent=get_llm_with_tools([bash_tool, edit_tool, grep_tool, glob_tool, ls_tool, multi_edit_tool, read_tool, write_tool,webfetch_tool,todo_write_tool])
        self.is_main=is_main
        self.toolset={
            "bash_tool":bash_tool,
            "edit_tool":edit_tool,
            "grep_tool":grep_tool,
            "glob_tool":glob_tool,
            "ls_tool":ls_tool,
            "multi_edit_tool":multi_edit_tool,
            "read_tool":read_tool,
            "write_tool":write_tool,
            "webfetch_tool":webfetch_tool,
            "websearch_tool":websearch_tool,
            "task_tool":task_tool,
            "todo_write_tool":todo_write_tool
        }
        self.message_history=[SystemMessage(content=get_character_info_prompt()),SystemMessage(content=sub_agent_system_prompt if not self.is_main else main_agent_system_prompt)]
        self.message_history.append(HumanMessage(content=system_reminder))
        self.todo_list:list[dict]=[]
        self.agent_type="MAIN AGENT" if self.is_main else "SUB AGENT"

    async def reason_and_act(self, query: str):
        self.message_history.append(HumanMessage(content=query))
        if len(self.todo_list)==0:
            self.message_history.append(HumanMessage(content=todo_list_reminder))
        while True:
            reasoning_result = await self.reasoning()
            if reasoning_result.tool_calls:
                # print(f"{YELLOW}OpenClaudeCode {self.agent_type} want to use the tools {reasoning_result.tool_calls}{RESET}\n")
                await self.acting(reasoning_result.tool_calls)
            else:
                break
        return reasoning_result.content

    async def reasoning(self):
        if self.is_main:
            llm = self.mainagent
        else:
            llm = self.subagent
        first = True
        print(f"{BLUE}OpenClaudeCode {self.agent_type} thinking...{RESET}\n")
        for chunk in llm.stream(self.message_history):
            if first:
                gathered = chunk
                first = False
            else:
                gathered = gathered + chunk
            print(chunk.content,end="",flush=True) if self.is_main else None
        self.message_history.append(AIMessage(content=gathered.content)) if gathered.content else None
        return gathered

    async def acting(self, tool_calls: list[dict]):
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_input = tool_call["args"]
            tool = self.toolset[tool_name]
            
            print(f"{CYAN}OpenClaudeCode {self.agent_type} wants to use tool {tool_name} with input {tool_input}{RESET}")
            user_choice = input(f"{YELLOW}Do you want to execute this tool? (y/n): {RESET}").strip().lower()
            
            if user_choice in ['y', 'yes']:
                print(f"{CYAN}OpenClaudeCode {self.agent_type} executing the tool {tool_name}{RESET}\n")
                result = tool.invoke(tool_input)
            else:
                print(f"{RED}Human rejected to run tool {tool_name}{RESET}\n")
                result = f"Human rejected to run this tool '{tool_name}' with arguments {tool_input}, try different tool or different input"
            print(f"{GREEN}OpenClaudeCode {self.agent_type }got the result {result}{RESET}\n")
            tool_message=result["content"] if isinstance(result,dict) else result
            # Handle todo_write_tool results by updating internal state
            if tool_name == "todo_write_tool" and hasattr(result, 'todos'):
                try:
                    # Parse the tool result content (assuming it's JSON)
                    import json
                    self.todo_list = result.todos
                    tool_message=get_todo_list_changed_reminder(self.todo_list)
                except (json.JSONDecodeError, AttributeError):
                    # If parsing fails, keep existing todo_list
                    pass
            
            self.message_history.append(ToolMessage(content=tool_message, tool_call_id=tool_call["id"]))