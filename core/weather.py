__version__ = "1.0.1"
__description__ = "Fetches the current weather. Works automatically for your IP's location or for a specific city name."
__author__ = "Souvik"
__website__ = ""

import urllib.request
import urllib.parse
import sys
import ssl

def main():
    # Force UTF-8 standard output to prevent 'charmap' encoding errors with emojis on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    city = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    url = f"https://wttr.in/{urllib.parse.quote(city)}?format=3" if city else "https://wttr.in/?format=3"
    
    try:
        # Create an unverified SSL context to fix macOS certificate errors
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
        with urllib.request.urlopen(req, context=context, timeout=5) as response:
            weather_data = response.read().decode('utf-8').strip()
            print(f"\x1b[36;1mWeather:\x1b[0m {weather_data}")
    except Exception as e:
        print(f"\x1b[31;1mError fetching weather:\x1b[0m {e}")

if __name__ == "__main__":
    main()