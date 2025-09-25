from app.LLM import get_llm_with_tools
from tools.writetool import write_tool

if __name__ == "__main__":
    query = "Write a file called test.txt with the content 'Hello, world!',before you start, you should thinking the reason why you want to write this file"
    llm = get_llm_with_tools([write_tool])
    first = True
    for chunk in llm.stream(query):
        if first:
            gathered = chunk
            first = False
        else:
            gathered = gathered + chunk
        print(chunk.content,end="",flush=True)
    if gathered.tool_calls:
        print(gathered.tool_calls)