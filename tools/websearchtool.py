from langchain_community.tools import DuckDuckGoSearchResults

websearch_tool=DuckDuckGoSearchResults(max_results=10,output_format="json")

if __name__ == "__main__":
    result = websearch_tool.invoke({"query": "What is the capital of France?"})
    print(result)