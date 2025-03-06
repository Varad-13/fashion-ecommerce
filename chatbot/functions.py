import requests

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_all_products",
            "description": "Fetches all products from the store for retrieval-augmented generation (RAG).",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    }
]

def get_all_products():
    response = requests.get("http://127.0.0.1:8000/api/products/")
    return response.json()