__version__ = "1.0.1"
__description__ = "Fetches and displays your public IP address, ISP, and geographical location."
__author__ = "Souvik"
__website__ = ""

import urllib.request
import json
import sys
import ssl

def main():
    url = "https://ipinfo.io/json"
    try:
        # Create an unverified SSL context to prevent macOS/Windows certificate errors
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
        with urllib.request.urlopen(req, context=context, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            print("\x1b[36;1m=== IP Information ===\x1b[0m")
            print(f"\x1b[32mIP:\x1b[0m       {data.get('ip', 'N/A')}")
            print(f"\x1b[32mCity:\x1b[0m     {data.get('city', 'N/A')}")
            print(f"\x1b[32mRegion:\x1b[0m   {data.get('region', 'N/A')}")
            print(f"\x1b[32mCountry:\x1b[0m  {data.get('country', 'N/A')}")
            print(f"\x1b[32mOrg:\x1b[0m      {data.get('org', 'N/A')}")
    except Exception as e:
        print(f"\x1b[31;1mError fetching IP info:\x1b[0m {e}")

if __name__ == "__main__":
    main()