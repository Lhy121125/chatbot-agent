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

def get_context(query):
    bm25 =  (
        client.query
        .get("Parts",["page_detail"])
        .with_bm25(query="How can I install part number PS11752778?")
        .with_limit(1)
        .do()
    )['data']['Get']['Parts'][0]['page_detail']

    hybrid =  (
        client.query
        .get("Parts",["page_detail"])
        .with_hybrid(query="How can I install part number PS11752778?", alpha=0.5)
        .with_limit(1)
        .do()
    )['data']['Get']['Parts'][0]['page_detail']

    res = f"""
    Here is the context using keyword search:
    {bm25}
    Here is the context using hybrid search:
    {hybrid}
    """
    return res



# print("==============================================================")

# similar_response = (
#     client.query
#     .get("Parts",["name","rating", "part_Select_Number", "description"])
#     .with_near_text({"concepts":["PS11752778"]})
#     .with_limit(3)
#     .do()
# )
# print(similar_response['data']['Get']['Parts'])

# print("==============================================================")

# key_search_response = (
#     client.query
#     .get("Parts",["name","rating", "part_Select_Number", "description"])
#     .with_bm25(query="How can I install part number PS11752778?")
#     .with_limit(3)
#     .do()
# )

# print(key_search_response['data']['Get']['Parts'])
# print("==============================================================")
# hybrid_response = (
#     client.query
#     .get("Parts",["name","rating", "part_Select_Number", "description"])
#     .with_hybrid(query="How can I install part number PS11752778?", alpha=0.5)
#     .with_limit(3)
#     .do()
# )
# print(hybrid_response['data']['Get']['Parts'])
# print("==============================================================")
res = get_context("How can I install part number PS11752778?")
print(res)
print(len(res))
