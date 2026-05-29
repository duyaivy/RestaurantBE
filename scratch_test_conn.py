import os
import httpx
import urllib.request
import ssl

print("--- ENVIRONMENT PROXIES ---")
for env in ["http_proxy", "https_proxy", "all_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"]:
    print(f"{env}: {os.environ.get(env)}")

print("\n--- TESTING URLLIB GET to google.com ---")
try:
    with urllib.request.urlopen("https://www.google.com", timeout=5) as response:
        print("urllib google.com status:", response.status)
except Exception as e:
    print("urllib google.com failed:", e)

print("\n--- TESTING URLLIB GET to generativelanguage.googleapis.com ---")
try:
    with urllib.request.urlopen("https://generativelanguage.googleapis.com/", timeout=5) as response:
        print("urllib gemini api status:", response.status)
except Exception as e:
    print("urllib gemini api failed:", e)

print("\n--- TESTING HTTPX GET to google.com ---")
try:
    resp = httpx.get("https://www.google.com", timeout=5)
    print("httpx google.com status:", resp.status_code)
except Exception as e:
    print("httpx google.com failed:", e)

print("\n--- TESTING HTTPX GET to generativelanguage.googleapis.com ---")
try:
    resp = httpx.get("https://generativelanguage.googleapis.com/", timeout=5)
    print("httpx gemini api status:", resp.status_code)
except Exception as e:
    print("httpx gemini api failed:", e)
