import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("CHATBOT_EMBEDDING_API_KEY")

def inspect_timeout(timeout_val):
    print(f"\n--- Testing with HttpOptions(timeout={timeout_val}) ---")
    client = genai.Client(api_key=key)
    original_send = client._api_client._httpx_client.send

    def custom_send(request, *args, **kwargs):
        print("x-server-timeout header:", request.headers.get("x-server-timeout"))
        print("http client timeout:", client._api_client._httpx_client.timeout)
        # return a mock response to avoid making the actual network call if we only want to see headers
        # but let's actually make the call with a mock response or just call original_send
        return original_send(request, *args, **kwargs)

    client._api_client._httpx_client.send = custom_send

    try:
        client.models.embed_content(
            model="gemini-embedding-001",
            contents="Hello",
            config=types.EmbedContentConfig(
                output_dimensionality=768,
                http_options=types.HttpOptions(timeout=timeout_val) if timeout_val is not None else None
            )
        )
        print("Success!")
    except Exception as e:
        print("Failed with:", e)

inspect_timeout(None)
inspect_timeout(30.0)
inspect_timeout(15)
inspect_timeout(300)
inspect_timeout(30000)
