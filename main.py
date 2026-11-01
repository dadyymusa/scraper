import os
import requests

def main():
    url = "https://books.toscrape.com/catalogue/page-1.html" # or the target URL for your task
    cache_path = "cache/catalogue-page-1.html"
    
    
    headers = {
        "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/dadyymusa/scraper.git)"
    }


    if os.path.exists(cache_path):
        print("CACHE HIT")
        with open(cache_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        print(f"Response size: {len(html_content)} bytes")
    else:
        print("FETCH")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                html_content = response.text
                
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                
                print(f"Response size: {len(html_content)} bytes")
            else:
                print(f"Failed to fetch. Status code: {response.status_code}")
        except requests.exceptions.Timeout:
            print("The request timed out.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()