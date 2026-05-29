import os
import time
import traceback
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("CHATBOT_EMBEDDING_API_KEY")
print("Using key:", key[:10] + "..." if key else "None")

# Test 3: SDK call with traceback
print("\n--- Test 3: SDK Call ---")
start = time.time()
try:
    client = genai.Client(api_key=key)
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents="Hello world",
        config=types.EmbedContentConfig(
            output_dimensionality=768,
            http_options=types.HttpOptions(timeout=10.0)
        )
    )
    print(f"SDK Succeeded in {time.time() - start:.2f}s")
except Exception as e:
    print(f"SDK Failed in {time.time() - start:.2f}s with error: {e}")
    traceback.print_exc()
