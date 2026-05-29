import os
import httpx
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

keys = {
    "CHATBOT_EMBEDDING_API_KEY": os.getenv("CHATBOT_EMBEDDING_API_KEY"),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
}

for name, key in keys.items():
    print(f"\n--- Testing with key from {name} ---")
    if not key:
        print("Key is empty, skipping.")
        continue
    print("Key prefix:", key[:10])
    
    # Let's test direct HTTPX request first
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "content": {
            "parts": [{"text": "Hello world"}]
        }
    }
    
    try:
        print("Sending direct HTTPX POST request to Google API...")
        r = httpx.post(url, json=data, headers=headers, timeout=10)
        print("HTTPX status code:", r.status_code)
        if r.status_code == 200:
            print("HTTPX Response JSON keys:", r.json().keys())
        else:
            print("HTTPX Error Response:", r.text)
    except Exception as e:
        print("HTTPX request failed:", e)

    # Let's test SDK client request
    try:
        print("Sending SDK client request...")
        client = genai.Client(api_key=key)
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents="Hello world",
            config=types.EmbedContentConfig(
                output_dimensionality=768,
                http_options=types.HttpOptions(timeout=10)
            )
        )
        embedding = response.embeddings[0].values
        print("SDK Success! Dimension size:", len(embedding))
    except Exception as e:
        print("SDK request failed:", e)
