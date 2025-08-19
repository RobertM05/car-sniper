import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.olx.ro/oferte/q-{}"

def scrape_olx(query: str, page: int = 1, limit: int = 10):
    """
    Scraper pentru OLX.
    Returneaza o lista de anunturi (titlu, pret, link).
    """
    url = BASE_URL.format(query.replace(" ", "-")) + f"/?page={page}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    ads = []

    for item in soup.select("div.css-1sw7q4x"):
        title_tag = item.select_one("h6.css-16v5mdi")
        price_tag = item.select_one("p.css-10b0gli")
        link_tag = item.select_one("a")

        if title_tag and price_tag and link_tag:
            ads.append({
                "title": title_tag.get_text(strip=True),
                "price": price_tag.get_text(strip=True),
                "link": "https://www.olx.ro" + link_tag["href"],
            })

        if len(ads) >= limit:
            break

    return ads
