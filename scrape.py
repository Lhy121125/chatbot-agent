import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from langchain.docstore.document import Document
from models import *
from llama_index.readers.web import UnstructuredURLLoader
import json

def gather_urls(url, parent_url):
    """
    Given a url, get all the urls at a particular place.
    """
    urls = set()
    urls.add(url)
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return urls

    try:
        soup = BeautifulSoup(resp.text, "html.parser")
        main_container = soup.find('main')
        if main_container is None:
            raise ValueError("Main container not found")

        urls.add(url)  # Append the original URL if needed

        types = main_container.find_all('ul', class_='nf__links')
        
        for ul in types:
            list_items = ul.find_all('li')
            for li in list_items:
                try:
                    a = li.find('a')
                    if a and 'href' in a.attrs:
                        # Append the full URL if not present
                        full_url = parent_url + a.attrs['href']
                        urls.add(full_url)
                except Exception as e:
                    print(f"Error processing an anchor tag: {e}")
                    continue 

    except Exception as e:
        print(f"Error parsing HTML for {url}: {e}")

    return list(urls)

def get_model_page(model_number):
    """
    Given a url, return the url of the model
    base_url should be https://www.partselect.com/Models/
    """
    pass

def read_page(url):
    """
    Given a url, collect all the information from the page
    """
    urls = [url]
    loader = UnstructuredURLLoader(urls)
    docs = loader.load_data()
    return docs[0].text


def collect_items(url, parent_url, visited_part):
    """
    Given a url, collect items from the page following the logic.
    """
    parts = []
    print(f"Collecting items from {url}")
    try:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")

        main_container = soup.find('main')
        if main_container is None:
            return parts  # Main container not found

        title = main_container.find('h2')
        if title is None:
            return parts  # Title not found
        
        for sibling in title.find_next_siblings():
            if sibling.name != 'div':
                break
            try:
                price = sibling.find('div', class_="mt-sm-2 price").text
                name_and_link = sibling.find('a', class_="nf__part__detail__title")
                name = name_and_link.text
                link = name_and_link.get('href')
                rating = sibling.find('a', class_="nf__part__detail__rating").get('alt')
                num_reviews = sibling.find('a', class_="nf__part__detail__rating").find('span').text
                Part_Select_Number = sibling.find('div', class_="nf__part__detail__part-number").find('strong').text
                Manufacturer_Part_Number = sibling.find('div', class_="nf__part__detail__part-number mb-2").find('strong')
                description = Manufacturer_Part_Number.find_next_sibling(text=True)
                page_detail = read_page(parent_url + link)

                if Part_Select_Number in visited_part:
                    continue

                part = Part(price, name, parent_url + link, rating, num_reviews, Part_Select_Number, Manufacturer_Part_Number.text, description, page_detail)
                parts.append(part)
                visited_part.add(Part_Select_Number)
                
                p = json.dumps(part.__dict__)
                # print(p)
                # print("====================================")
            except Exception as e:
                print(f"Error processing part: {e}")
                continue 

    except Exception as e:
        print(f"Error fetching or parsing {url}: {e}")

    return parts



# base_url = "https://www.partselect.com/Dishwasher-Parts.htm"
# parent_url = "https://www.partselect.com"
# urls = gather_urls(base_url, parent_url)
# visited_part = set()

# for url in urls:
#     print(f"URL: {url}")
#     print(collect_items(url, parent_url, visited_part))
# # print(read_page("https://www.partselect.com/PS10065979-Whirlpool-W10712395-Upper-Rack-Adjuster-Kit-White-Wheels-Left-and-Right-Sides.htm?SourceCode=18"))