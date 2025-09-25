from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv
import os
from langchain_core.tools import BaseTool
from typing import List
from config import model_config
from dataclasses import asdict
# load_dotenv()
# print(os.getenv("MODEL_NAME"))
# print(os.getenv("API_KEY"))
# print(os.getenv("BASE_URL"))
# llm = ChatOpenAI(model=os.getenv("MODEL_NAME"),api_key=os.getenv("API_KEY"),base_url=os.getenv("BASE_URL"))
llm = ChatOpenAI(model=model_config.model,api_key=model_config.api_key,base_url=model_config.base_url)
def get_llm():
    return llm

def get_llm_with_tools(tools: List[BaseTool]):
    return llm.bind_tools(tools)

if __name__ == "__main__":
    print(llm.invoke("Hello, how are you?"))