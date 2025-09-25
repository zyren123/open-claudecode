from app import ReactAgent
import asyncio
from prompt.system import default_params

def print_welcome():
    """打印欢迎信息和系统环境"""
    print("=" * 50)
    print("🚀 OpenClaudeCode - AI Coding Assistant")
    print("=" * 50)
    print(default_params)
    print("💡 输入 'exit', 'quit', 'bye', 或 'q' 退出程序")
    print("-" * 50)

agent=ReactAgent(is_main=True)

async def mainloop():
    print_welcome()
    
    while True:
        user_input=input("You: ")
        if user_input.lower() in ["exit","quit","bye","q"]:
            print("👋 Goodbye!")
            break
        response=await agent.reason_and_act(user_input)


if __name__ == "__main__":
    asyncio.run(mainloop())
