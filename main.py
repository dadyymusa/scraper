import os
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

def fetch_or_load_page(url, cache_path, headers):
    """Fetches a page with caching, polite delay, and status validation."""
    if os.path.exists(cache_path):
        print("CACHE HIT")
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read(), True
    else:
        print("FETCH")
        
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
    base_url = "https://books.toscrape.com/catalogue/"
    current_url = "https://books.toscrape.com/catalogue/page-1.html"
    
    headers = {
        "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/dadyymusa/scraper.git)"
    }

    catalogue_pages = 0
    all_book_urls = []
    
    page_num = 1
    while current_url and page_num <= 3:
        cache_path = f"cache/catalogue-page-{page_num}.html"
        
        html_content, from_cache = fetch_or_load_page(current_url, cache_path, headers)
        if not html_content:
            break
            
        catalogue_pages += 1
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        book_elements = soup.select("article.product_pod h3 a")
        for book in book_elements:
            href = book.get("href")
            absolute_url = urljoin(current_url, href)
            all_book_urls.append(absolute_url)

        next_button = soup.select_one("li.next > a")
        if next_button:
            next_href = next_button.get("href")
            current_url = urljoin(current_url, next_href)
            page_num += 1
        else:
            current_url = None 

    unique_urls = list(set(all_book_urls))
    
    print(f"catalogue_pages={catalogue_pages}, discovered={len(all_book_urls)}, unique_urls={len(unique_urls)}")

if __name__ == "__main__":
    main()