#!/usr/bin/env python3
"""
One-time LinkedIn OAuth authentication.
Run this once to get your access token saved to .env
"""

import http.server
import threading
import webbrowser
import urllib.parse
import requests
import json
from pathlib import Path
from dotenv import dotenv_values, set_key

config     = dotenv_values(Path.home() / ".env")
CLIENT_ID  = config.get("LINKEDIN_CLIENT_ID")
CLIENT_SEC = config.get("LINKEDIN_CLIENT_SECRET")
ENV_FILE   = Path.home() / ".env"

REDIRECT   = "http://localhost:8000/callback"
SCOPE      = "openid profile email w_member_social"
AUTH_URL   = (
    f"https://www.linkedin.com/oauth/v2/authorization"
    f"?response_type=code&client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT)}"
    f"&scope={urllib.parse.quote(SCOPE)}"
)

auth_code = None

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h2>LinkedIn connected! You can close this tab.</h2>")

    def log_message(self, *args):
        pass


def run():
    global auth_code

    server = http.server.HTTPServer(("localhost", 8000), CallbackHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.daemon = True
    thread.start()

    print("\n👉 Open this URL in your browser:\n")
    print(AUTH_URL)
    print("\nWaiting for LinkedIn login (120 seconds)...")
    thread.join(timeout=300)

    if not auth_code:
        print("No auth code received. Try again.")
        return

    # Exchange code for access token
    resp = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SEC,
        }
    )
    token_data = resp.json()
    access_token = token_data.get("access_token")

    if not access_token:
        print("Failed to get token:", token_data)
        return

    # Save token to .env
    set_key(str(ENV_FILE), "LINKEDIN_ACCESS_TOKEN", access_token)
    print("✅ LinkedIn connected! Access token saved to .env")

    # Verify by fetching profile
    profile = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()
    print(f"Logged in as: {profile.get('name')} ({profile.get('email')})")


if __name__ == "__main__":
    run()
