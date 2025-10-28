import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.olx.ro/oferte/q-{}"

def scrape_olx(
    query: str,
    page: int = 1,
    limit: int = 10,
    *,
    min_price: int | None = None,
    max_price: int | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    max_km: int | None = None,
):
 

    params = {"page": str(page)}
    if min_price is not None:
        params["search[filter_float_price:from]"] = str(min_price)
    if max_price is not None:
        params["search[filter_float_price:to]"] = str(max_price)
    if min_year is not None:
        params["search[filter_float_year:from]"] = str(min_year)
    if max_year is not None:
        params["search[filter_float_year:to]"] = str(max_year)
    if max_km is not None:
        params["search[filter_float_mileage:to]"] = str(max_km)

    url = BASE_URL.format(query.replace(" ", "-"))
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, params=params)
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
