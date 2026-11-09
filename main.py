import os
import time
import json
from datetime import datetime, timezone
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

def fetch_or_load_page(url, cache_path, headers):
    if os.path.exists(cache_path):
        print(f"CACHE HIT: {cache_path}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read(), True
    else:
        print(f"FETCH: {url}")
        time.sleep(0.5)
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                html_content = response.text
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                return html_content, False
            else:
                print(f"Failed to fetch {url}. Status code: {response.status_code}")
                return None, False
        except requests.exceptions.Timeout:
            print(f"Request timed out for {url}")
            return None, False
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None, False

def main():
    current_url = "https://books.toscrape.com/catalogue/page-1.html"
    headers = {
        "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/dadyymusa/scraper.git)"
    }

    book_entries = []
    page_num = 1
    
    while current_url and page_num <= 3:
        cache_path = f"cache/catalogue-page-{page_num}.html"
        html_content, _ = fetch_or_load_page(current_url, cache_path, headers)
        if not html_content:
            break
            
        soup = BeautifulSoup(html_content, "html.parser")
        book_elements = soup.select("article.product_pod h3 a")
        for book in book_elements:
            href = book.get("href")
            absolute_url = urljoin(current_url, href)
            book_entries.append((absolute_url, current_url))
            
        next_button = soup.select_one("li.next > a")
        if next_button:
            current_url = urljoin(current_url, next_button.get("href"))
            page_num += 1
        else:
            current_url = None

    seen = set()
    unique_books = []
    for abs_url, source_page in book_entries:
        if abs_url not in seen:
            seen.add(abs_url)
            unique_books.append((abs_url, source_page))

    records = []
    for book_url, source_page in unique_books:
        parts = [p for p in book_url.rstrip("/").split("/") if p]
        book_slug = parts[-2] if len(parts) >= 2 else parts[-1]
        detail_cache_path = f"cache/books/{book_slug}.html"
        
        detail_html, _ = fetch_or_load_page(book_url, detail_cache_path, headers)
        if not detail_html:
            continue
            
        soup = BeautifulSoup(detail_html, "html.parser")
        
        title_elem = soup.select_one("div.product_main h1")
        title = title_elem.text.strip() if title_elem else None
        
        price_elem = soup.select_one("p.price_color")
        price_text = price_elem.text.strip() if price_elem else None
        
        avail_elem = soup.select_one("p.instock.availability")
        availability_text = avail_elem.text.strip() if avail_elem else None
        
        rating_elem = soup.select_one("p.star-rating")
        rating_text = None
        if rating_elem and rating_elem.get("class"):
            classes = rating_elem.get("class")
            rating_text = next((c for c in classes if c != "star-rating"), None)
            
        desc_elem = soup.select_one("div#product_description ~ p")
        description = desc_elem.text.strip() if desc_elem else None
        
        fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        record = {
            "title": title,
            "product_url": book_url,
            "price_text": price_text,
            "availability_text": availability_text,
            "rating_text": rating_text,
            "description": description,
            "source_page": source_page,
            "fetched_at": fetched_at
        }
        records.append(record)

    if records:
        print("\n--- Sample Complete Raw Record ---")
        print(json.dumps(records[0], indent=2))
        print("-----------------------------------\n")

    print(f"detail_pages={len(records)}")

if __name__ == "__main__":
    main()