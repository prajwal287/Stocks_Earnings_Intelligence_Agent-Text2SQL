import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")

if not API_KEY:
    print("❌ API_KEY not found in .env")
    exit()

print(f"Testing Polygon.io endpoints with your API key...\n")

endpoints = [
    ("Stock Aggregates (OHLC)", f"https://api.polygon.io/v2/aggs/ticker/MSFT/range/1/day/2024-01-01/2024-12-31?apikey={API_KEY}"),
    ("Stock Quotes", f"https://api.polygon.io/v3/quotes/MSFT?apikey={API_KEY}"),
    ("Ticker Details", f"https://api.polygon.io/v3/reference/tickers/MSFT?apikey={API_KEY}"),
    ("Previous Close", f"https://api.polygon.io/v2/aggs/ticker/MSFT/prev?apikey={API_KEY}"),
]

for name, url in endpoints:
    try:
        response = requests.get(url, timeout=5)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {name}: HTTP {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            if 'results' in data:
                print(f"   Data points: {len(data.get('results', []))}")
    except Exception as e:
        print(f"❌ {name}: {str(e)[:50]}")

print("\n" + "="*60)
print("Which endpoint has a ✅ next to it?")
print("That's the one we should use!")
