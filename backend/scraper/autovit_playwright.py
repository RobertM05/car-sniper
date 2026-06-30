import asyncio
import json
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


async def scrape_autovit_playwright(
    make: str,
    model: str,
    limit: int = 100,
    max_pages: int = 10,
    *,
    min_price: int | None = None,
    max_price: int | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    max_km: int | None = None,
    generation: str | None = None,
) -> list[dict]:
    results = []
    seen_links = set()
    base_url = f"https://www.autovit.ro/autoturisme/{make.lower()}/{model.lower()}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ro-RO",
        )
        page = await context.new_page()
        for page_num in range(1, max_pages + 1):
            if len(results) >= limit:
                break
            params = [f"page={page_num}"]
            if max_price is not None:
                params.append(f"search[filter_float_price:to]={max_price}")
            if min_price is not None:
                params.append(f"search[filter_float_price:from]={min_price}")
            if min_year is not None:
                params.append(f"search[filter_float_year:from]={min_year}")
            if max_year is not None:
                params.append(f"search[filter_float_year:to]={max_year}")
            if max_km is not None:
                params.append(f"search[filter_float_mileage:to]={max_km}")
            if generation:
                params.append(f"search[filter_enum_generation]={generation}")
                params.append("search[advanced_search_expanded]=true")
            url = f"{base_url}?{'&'.join(params)}"
            try:
                print(f"Playwright: Loading page {page_num}...")
                await page.goto(url, timeout=30000)
                await page.wait_for_load_state("networkidle")
                json_ld_script = await page.query_selector("script#__NEXT_DATA__")
                html_links = []
                link_elements = await page.query_selector_all('a[href*=".html"]')
                for le in link_elements:
                    href = await le.get_attribute("href")
                    if href and "anunt" in href:
                        if href.startswith("/"):
                            href = "https://www.autovit.ro" + href
                        if href not in html_links:
                            html_links.append(href)
                page_results_before = len(results)
                if json_ld_script:
                    json_text = await json_ld_script.inner_text()
                    try:
                        data = json.loads(json_text)
                        items = data.get("mainEntity", {}).get("itemListElement", [])
                        print(
                            f"   JSON-LD: {len(items)} items, HTML: {len(html_links)} links"
                        )
                        for idx, elem in enumerate(items):
                            if len(results) >= limit:
                                break
                            item = elem.get("itemOffered", {})
                            name = item.get("name")
                            if not name:
                                continue
                            price_spec = elem.get("priceSpecification", {})
                            price_raw = price_spec.get("price")
                            if idx < len(html_links):
                                link = html_links[idx]
                            else:
                                link = item.get("url") or elem.get("url") or ""
                                if link.startswith("/"):
                                    link = "https://www.autovit.ro" + link
                            if link in seen_links:
                                continue
                            seen_links.add(link)
                            img_url = item.get("image")
                            if isinstance(img_url, list) and img_url:
                                img_url = img_url[0]
                            if price_raw:
                                try:
                                    final_price = int(float(price_raw))
                                    results.append(
                                        {
                                            "title": name,
                                            "price": f"{final_price} €",
                                            "link": link,
                                            "image": img_url,
                                            "subsource": "Autovit",
                                        }
                                    )
                                except Exception:
                                    pass
                    except json.JSONDecodeError:
                        print("   Failed to parse JSON-LD")
                else:
                    print("   No JSON-LD found")
                    for link in html_links:
                        if len(results) >= limit:
                            break
                        if link in seen_links:
                            continue
                        seen_links.add(link)
                        results.append(
                            {
                                "title": "Autovit Ad",
                                "price": "N/A €",
                                "link": link,
                                "image": None,
                                "subsource": "Autovit",
                            }
                        )
                new_results = len(results) - page_results_before
                print(f"   Added {new_results} new results (total: {len(results)})")
                if new_results == 0:
                    print("   No new results, stopping")
                    break
            except PlaywrightTimeout:
                print(f"Timeout on page {page_num}")
                continue
            except Exception as e:
                print(f"Error on page {page_num}: {e}")
                continue
            await asyncio.sleep(1)
        ads_without_image = [r for r in results if not r.get("image")]
        if ads_without_image:
            print(f"Fetching images for {len(ads_without_image)} ads without images...")

            async def fetch_image_for_ad(ad):
                try:
                    ad_page = await context.new_page()
                    await ad_page.goto(ad["link"], timeout=15000)
                    await ad_page.wait_for_load_state("domcontentloaded")
                    og_img = await ad_page.query_selector('meta[property="og:image"]')
                    if og_img:
                        content = await og_img.get_attribute("content")
                        if content:
                            ad["image"] = content
                            await ad_page.close()
                            return
                    img_selectors = [
                        'img[src*="ireland.apollo"]',
                        'div[class*="gallery"] img',
                        'div[class*="photo"] img',
                        'img[src*="autovit"]',
                    ]
                    for sel in img_selectors:
                        img = await ad_page.query_selector(sel)
                        if img:
                            src = await img.get_attribute("src")
                            if src:
                                ad["image"] = src
                                break
                    await ad_page.close()
                except Exception:
                    pass

            batch_size = 5
            for i in range(0, len(ads_without_image), batch_size):
                batch = ads_without_image[i : i + batch_size]
                await asyncio.gather(*[fetch_image_for_ad(ad) for ad in batch])
                await asyncio.sleep(0.3)
            fetched = sum((1 for r in results if r.get("image")))
            print(f"   Images now: {fetched}/{len(results)}")
        await browser.close()
    print(f"Playwright: Total {len(results)} results")
    return results


async def test():
    results = await scrape_autovit_playwright(
        make="bmw", model="x6", limit=100, max_pages=5
    )
    print(f"\nGot {len(results)} results")
    for r in results[:10]:
        print(f"  {r['title'][:45]} | {r['price']}")


if __name__ == "__main__":
    asyncio.run(test())
