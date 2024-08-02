import requests
from functools import lru_cache
from bs4 import BeautifulSoup

@lru_cache(maxsize=50)
def web_search(query):
    if 'formula' in query or 'công thức' in query:
        url = f"https://www.google.com/search?q={query}+formula"
    else:
        url = f"https://www.google.com/search?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('div', class_='g')
    return results[0].get_text() if results else None