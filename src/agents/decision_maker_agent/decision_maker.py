import os 
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from src.tools.react_tool import merge_decision_tool

load_dotenv()

# Load environment variables from .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY is not set in the .env file.")
    
llm = ChatOpenAI(model="gpt-4o", temperature=0)
tools = [merge_decision_tool]
react_agent_executor = create_react_agent(llm, tools=tools)

async def run_react_agent(code_analysis: str, review_comments: list) -> str:

    comments_str = "\n".join(
        [f"- [{c.get('comment_type', '').upper()}] {c.get('content', '')}" for c in review_comments]
    )
    query = (
        f"You are a senior software engineer evaluating a pull request.\n\n"
        f"Code Analysis:\n{code_analysis}\n\n"
        f"Review Comments:\n{comments_str}\n\n"
        "Make a merge decision. You MUST reply using one of these formats only:\n"
        "- YES, it is safe to merge. [brief reason]\n"
        "- NO, do not merge. [brief reason]\n"
    )
    result = await react_agent_executor.ainvoke({"messages": [("human", query)]})
    messages = result["messages"]
    return messages[-1].content if messages else "No decision made."