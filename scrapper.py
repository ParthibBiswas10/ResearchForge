import os

import requests
from dotenv import load_dotenv
from langchain.tools import tool
from bs4 import BeautifulSoup
load_dotenv()
from rich import print

