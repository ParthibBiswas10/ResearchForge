import os

import requests
from dotenv import load_dotenv
from langchain.tools import tool
from bs4 import BeautifulSoup
load_dotenv()
from rich import print

@tool
def scrape(url:str)->str:
    """Fetch a web page and return a cleaned text excerpt."""
    try:
        resp=requests.get(url,timeout=8,headers={"User-Agent":"Mozilla/5.0"})

        soup=BeautifulSoup(resp.text,"html.parser")
        for tag in soup(["script","div","header","footer","nav"]):
            tag.decompose()

        return soup.get_text(separator=" ",strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape url: {str(e)}"

print(scrape.invoke("https://timesofindia.indiatimes.com/sports/football/top-stories/the-impossible-messi-and-ronaldo-could-finally-play-together-on-same-team-after-special-invite-from-former-teammate/articleshow/133798533.cms"))    


"""requests.get()

#equests is a Python library used to send HTTP requests to websites."""