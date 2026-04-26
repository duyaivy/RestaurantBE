import os
import django
from django.core.cache import cache

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantBE.settings.local')
django.setup()

def test_redis():
    print("Testing Redis connectivity...")
    try:
        cache.set('test_key', 'hello_redis', timeout=30)
        value = cache.get('test_key')
        if value == 'hello_redis':
            print("Successfully connected to Redis!")
            cache.delete('test_key')
        else:
            print(f"Failed: Unexpected value from Redis: {value}")
    except Exception as e:
        print(f"Failed: Error connecting to Redis: {e}")

if __name__ == "__main__":
    test_redis()
