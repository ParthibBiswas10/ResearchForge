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

    results = response.get("results", []) if isinstance(response, dict) else []
    if not results:
        return "No results found."
    
    output = []
    for item in results:
        title = item.get("title", "Untitled")
        url = item.get("url", "")
        content = item.get("content", "")
        output.append(f"{title}\n{url}\n{content[:500]}\n")

    return "\n".join(output)



print(web_search.invoke("what are the recent news of Messi?"))

@tool
def scrape(url:str)->str:
    """Fetch a web page and return a cleaned text excerpt."""
    try:
        resp=requests.get(url,timeout=8,headers={"User-Agent":"Mozilla/5.0"})

        soup=BeautifulSoup(resp.text,"html.parser")
        for tag in soup(["script","header","footer","nav"]):
            tag.decompose()

        return soup.get_text(separator=" ",strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape url: {str(e)}"

print(scrape.invoke("https://timesofindia.indiatimes.com/sports/football/top-stories/the-impossible-messi-and-ronaldo-could-finally-play-together-on-same-team-after-special-invite-from-former-teammate/articleshow/133798533.cms"))    


"""
resp is the Response object holding the status code, headers, and body (resp.text is the HTML as a string).


requests.get()

#equests is a Python library used to send HTTP requests to websites.

soup = BeautifulSoup(resp.text, "html.parser")

It tells BeautifulSoup how to read/parse the HTML.
Think of it like this: before this line, you just have a blob of text that looks like HTML. After this line, Python actually understands its structure — which tags are nested inside which, what their attributes are, and so on — so you can query it programmatically instead of manually searching through a string.

Think of it like:

BeautifulSoup(HTML, "HOW SHOULD I READ THIS?")

So:

BeautifulSoup(resp.text, "html.parser")

means:

"Take this HTML (resp.text) and understand its structure using Python's built-in HTML parser."

.get_text() is a BeautifulSoup method that extracts the text from HTML.
"""