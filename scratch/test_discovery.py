import urllib.request
import json
import ssl
import time

topic = "tor_chat_global_rooms_v2"
url = f"https://ntfy.sh/{topic}/json?poll=1"
print(f"Polling {url}...")

try:
    context = ssl._create_unverified_context()
    resp = urllib.request.urlopen(url, context=context)
    data = resp.read().decode('utf-8')
    messages = [json.loads(line) for line in data.strip().split('\n') if line]
    
    count = 0
    for evt in messages:
        if 'message' in evt:
            print(f"Found message: {evt['message']}")
            count += 1
    
    if count == 0:
        print("No historical messages found on this topic.")
except Exception as e:
    print(f"Error: {e}")
