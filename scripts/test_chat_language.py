import os
import sys
import django
from dotenv import load_dotenv

load_dotenv()

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurantBE.settings.local")
django.setup()

from restaurantBE.chatbot.rag.chat import ChatService

def main():
    service = ChatService()
    
    # 1. Test English question
    eng_query = "Hello, what is your address and how much do the Spring rolls cost?"
    print(f"User (EN): {eng_query}")
    res_en = service.reply(eng_query, lang="en")
    print(f"Bot (EN) : {res_en['answer']}")
    print(f"Items (EN): {res_en['items']}")
    print("-" * 50)
    
    # 2. Test Vietnamese question
    vi_query = "Xin chào, địa chỉ quán ở đâu và chả giò giá bao nhiêu vậy?"
    print(f"User (VI): {vi_query}")
    res_vi = service.reply(vi_query, lang="vi")
    print(f"Bot (VI) : {res_vi['answer']}")
    print(f"Items (VI): {res_vi['items']}")
    print("-" * 50)

if __name__ == "__main__":
    main()
