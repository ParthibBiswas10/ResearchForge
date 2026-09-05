import os

from dotenv import load_dotenv
from langchain.tools import tool

try:
    from tavily import TavilyClient
except ImportError:  # pragma: no cover - only used if dependency is missing
    TavilyClient = None

load_dotenv()


def _get_tavily_client():
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY is not set. Add it to your .env file."
        )
    if TavilyClient is None:
        raise ImportError("tavily-python is not installed. Please install requirements.txt.")
    return TavilyClient(api_key=api_key)


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic."""
    try:
        tavily = _get_tavily_client()
        response = tavily.search(query=query, max_results=5)
    except Exception as exc:  
        return f"Search failed: {exc}"


print(web_search.invoke("what are the recent news of Messi?"))
