from bs4 import BeautifulSoup as Soup
from urllib.parse import urljoin, urlparse
from collections import deque
import threading
import requests

def is_valid_url(url):
    """
    """
    return True

def get_urls(base_url, depth=0):
    """
    BFS function to go through the information
    """
    visited = set()
    to_visit = deque([(base_url, 0)])
    all_urls = set()

    while to_visit and len(all_urls) < 150:
        current_url, current_depth = to_visit.popleft()
        print(f"Visiting {current_url} at depth {current_depth}")
        if current_url in visited or current_depth > depth:
            continue
        visited.add(current_url)

        try:
            response = requests.get(current_url, timeout=2)  # Add a timeout for efficiency

            content_type = response.headers.get('Content-Type', '')
            # Only process if content type is HTML, for example
            if 'text/html' in content_type:
                soup = Soup(response.text, "html.parser")
                # Your processing logic here
            else:
                print(f"Skipping unsupported content type at {current_url}: {content_type}")
                continue  # Skip further processing and go to the next URL


            # soup = Soup(response.text, "html.parser")
            for link in soup.find_all('a', href=True):
                href = link['href']
                abs_url = urljoin(current_url, href)
                if is_valid_url(abs_url) and abs_url not in visited:
                    all_urls.add(abs_url)
                    if current_depth < depth:
                        to_visit.append((abs_url, current_depth + 1))
        except Exception as e:
            print(f"Failed to fetch {current_url}: {e}")

    return list(all_urls)

base_url = "https://www.partselect.com/Refrigerator-Parts.htm"
urls = get_urls(base_url, depth=0)
print(f"Found {len(urls)} URLs")
for url in urls:
    print(url)