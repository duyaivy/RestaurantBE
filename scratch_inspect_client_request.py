import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("CHATBOT_EMBEDDING_API_KEY")
client = genai.Client(api_key=key)

# Mock/wrap send method of the httpx client to inspect the outgoing request
original_send = client._api_client._httpx_client.send

def custom_send(request, *args, **kwargs):
    print("\n--- Outgoing SDK Request ---")
    print("Method:", request.method)
    print("URL:", request.url)
    print("Headers:")
    for k, v in request.headers.items():
        # Mask api key in logs
        val = v
        if "key" in k.lower() or "authorization" in k.lower():
            val = v[:10] + "..."
        print(f"  {k}: {val}")
    return original_send(request, *args, **kwargs)

client._api_client._httpx_client.send = custom_send

try:
    client.models.embed_content(
        model="gemini-embedding-001",
        contents="Hello world",
        config=types.EmbedContentConfig(
            output_dimensionality=768,
            http_options=types.HttpOptions(timeout=5.0)
        )
    )
except Exception as e:
    print("\nRequest failed with:", e)
