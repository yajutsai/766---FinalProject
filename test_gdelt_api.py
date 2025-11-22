"""
測試 GDELT API 連接和響應格式
"""

import requests
import json

BASE_URL = 'https://api.gdeltproject.org/api/v2/doc/doc'

# Test query (GDELT requires OR queries to be wrapped in parentheses)
keywords = ["bitcoin", "btc", "ethereum", "eth"]
query = f"({' OR '.join(keywords)})"

params = {
    'query': query,
    'mode': 'artlist',
    'maxrecords': 10,  # Just test with 10 records
    'format': 'json',
    'startdatetime': '20241101000000',
    'enddatetime': '20241110000000'  # Just test with a small date range
}

print("Testing GDELT API...")
print(f"URL: {BASE_URL}")
print(f"Query: {query}")
print(f"Date range: 2024-11-01 to 2024-11-10")
print()

try:
    response = requests.get(BASE_URL, params=params, timeout=30)
    print(f"Status code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
    print()
    
    if response.status_code == 200:
        content = response.text.strip()
        print(f"Response length: {len(content)} characters")
        print(f"First 500 characters:")
        print(content[:500])
        print()
        
        # Try to parse
        try:
            if content.startswith('['):
                data = json.loads(content)
                print(f"Parsed as JSON array: {len(data)} items")
                if len(data) > 0:
                    print(f"\nFirst item structure:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False)[:1000])
            elif content.startswith('{'):
                data = json.loads(content)
                print(f"Parsed as JSON object")
                print(f"Keys: {list(data.keys())}")
            else:
                # Try JSON Lines
                lines = content.split('\n')
                print(f"Trying JSON Lines format: {len(lines)} lines")
                if len(lines) > 0:
                    try:
                        first_item = json.loads(lines[0])
                        print(f"First line parsed successfully")
                        print(f"Keys: {list(first_item.keys())}")
                    except:
                        print("Could not parse first line as JSON")
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
    else:
        print(f"Error response: {response.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

