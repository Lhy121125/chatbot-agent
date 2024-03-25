import weaviate, os
from weaviate import EmbeddedOptions
import openai
from scrape import *

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

client = weaviate.Client(
    url = os.environ['WEAVIATE_URL'],
    auth_client_secret=weaviate.auth.AuthApiKey(os.environ['WEAVIATE_API_KEY']),
)
client = weaviate.Client(
    embedded_options=EmbeddedOptions(),
    additional_headers={
        "X-OpenAI-Api-Key": openai.api_key 
    }
)
print(f"Client Ready? {client.is_ready()}")

# resetting the schema. CAUTION: This will delete your collection 
if client.schema.exists("Parts"):
    client.schema.delete_class("Parts")
class_obj = {
    "class": "Parts",
    "vectorizer": "text2vec-openai",  # Use OpenAI as the vectorizer
    "moduleConfig": {
        "text2vec-openai": {
            "model": "ada",
            "modelVersion": "002",
            "type": "text"
        }
    }
}
client.schema.create_class(class_obj)
client.batch.configure(
  batch_size=50,
  num_workers=2
)

def load_data(url, parent_url):
    """
    This function collect all the parts and store it into a db
    """
    urls = gather_urls(url, parent_url)
    visited_part = set()
    all_parts = []
    for url in urls:
        items = collect_items(url, parent_url, visited_part)
        all_parts.extend(items)
    
    with client.batch as batch:
        for i, part in enumerate(all_parts):
            print(f"adding part: {i+1}")
            batch.add_data_object(
                data_object=part.__dict__,
                class_name="Parts",
            )
    
    count = client.query.aggregate("Parts").with_meta_count().do()
    print(count)


base_url = "https://www.partselect.com/Dishwasher-Parts.htm"
parent_url = "https://www.partselect.com"
load_data(base_url, parent_url)

base_url_fridge = "https://www.partselect.com/Refrigerator-Parts.htm"
load_data(base_url_fridge, parent_url)
