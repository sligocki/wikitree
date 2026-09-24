import argparse
import getpass
import http.cookiejar
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://api.wikitree.com/api.php"

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Do not redirect

def main():
    parser = argparse.ArgumentParser(description="Download your WikiTree Watchlist.")
    parser.add_argument("--email", required=True, help="WikiTree login email")
    parser.add_argument("--output", default="data/watchlist.json", help="Output file")
    parser.add_argument("--limit", type=int, default=1000, help="Pagination limit")
    args = parser.parse_args()

    password = getpass.getpass("WikiTree Password: ")

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        NoRedirectHandler(),
        urllib.request.HTTPCookieProcessor(cj)
    )
    urllib.request.install_opener(opener)

    print("Logging in...")
    post_data = urllib.parse.urlencode({
        "action": "clientLogin",
        "doLogin": 1,
        "wpEmail": args.email,
        "wpPassword": password,
    }).encode("utf-8")

    req = urllib.request.Request(API_URL, data=post_data)
    location = None
    try:
        resp = urllib.request.urlopen(req)
        # If credentials are wrong, it might return 200 with the login page HTML
        location = resp.headers.get("Location")
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307):
            location = e.headers.get("Location")
        else:
            sys.exit(f"Login error: HTTP {e.code}")

    if not location:
        sys.exit("Login failed. Please check your credentials (expected a redirect).")

    match = re.search(r"authcode=([^&]+)", location)
    if not match:
        sys.exit("Login failed. No authcode in redirect. Please check your credentials.")

    authcode = match.group(1)

    # Complete login with authcode
    post_data = urllib.parse.urlencode({
        "action": "clientLogin",
        "authcode": authcode
    }).encode("utf-8")
    
    req = urllib.request.Request(API_URL, data=post_data)
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        sys.exit(f"Authentication completion failed: HTTP {e.code}")
        
    print("Login successful! Downloading watchlist...")
    
    # Restore normal redirect handling for future requests
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    urllib.request.install_opener(opener)

    offset = 0
    full_watchlist = []
    
    while True:
        print(f"Fetching from offset {offset}...")
        params = urllib.parse.urlencode({
            "action": "getWatchlist",
            "getPerson": "1",
            "limit": args.limit,
            "offset": offset,
        }).encode("utf-8")
        
        req = urllib.request.Request(API_URL, data=params)
        try:
            r = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            sys.exit(f"Failed to fetch watchlist: HTTP {e.code}")
            
        data = json.loads(r.read().decode("utf-8"))
        
        if isinstance(data, list):
            resp_data = data[0].get("getWatchlist", data[0])
        else:
            resp_data = data.get("getWatchlist", data)
            
        if "watchlist" not in resp_data:
            print(f"Unexpected response: {resp_data}")
            break
            
        batch = resp_data["watchlist"]
        if isinstance(batch, dict):
            batch = list(batch.values())
            
        full_watchlist.extend(batch)
        
        if len(batch) < args.limit:
            break
            
        offset += args.limit
        
    print(f"Downloaded {len(full_watchlist)} profiles.")
    
    output_data = [{
        "watchlistCount": len(full_watchlist),
        "watchlist": full_watchlist
    }]
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Watchlist saved to {output_path}")

if __name__ == "__main__":
    main()
