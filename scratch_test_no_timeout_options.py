import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("CHATBOT_EMBEDDING_API_KEY")

client = genai.Client(api_key=key)

try:
    print("Calling embed_content with NO custom timeout/http_options...")
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents="Hello world",
    )
    embedding = response.embeddings[0].values
    print("Success! Embedding length:", len(embedding))
except Exception as e:
    print("Failed:", e)
