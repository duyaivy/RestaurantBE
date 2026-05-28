import os
import sys
import django
from dotenv import load_dotenv

load_dotenv()

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurantBE.settings.local")
django.setup()

from restaurantBE.chatbot.rag.retrieval import RetrievalService

def main():
    service = RetrievalService()
    
    queries = [
        "Hello, what is your address and how much do the Spring rolls cost?",
        "Xin chào, địa chỉ quán ở đâu và chả giò giá bao nhiêu vậy?",
        "What is your address?",
        "Where is the restaurant located?",
        "Do you have spring rolls?",
        "chả giò"
    ]
    
    for q in queries:
        print(f"\nQUERY: {q}")
        results = service.search(q, top_k=5)
        print(f"Found {len(results)} results:")
        for idx, r in enumerate(results):
            meta = r.get("metadata", {})
            dist = r.get("distance")
            dist_str = f"{dist:.4f}" if dist is not None else "None"
            content = r.get("content", "")
            source = meta.get("source", "unknown")
            print(f"  [{idx}] source={source}, distance={dist_str}")
            print(f"      Content summary: {content[:150].replace(chr(10), ' ')}")

if __name__ == "__main__":
    main()
