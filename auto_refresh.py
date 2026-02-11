import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ACCOUNTS_URL = os.getenv("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.com")

def refresh_access_token():
    if not REFRESH_TOKEN:
        print("[ERROR] No Refresh Token found in .env. Please run get_tokens.py first!")
        return

    url = f"{ACCOUNTS_URL}/oauth/v2/token"
    params = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN
    }

    try:
        print(f"[INFO] Requesting new Access Token using Refresh Token...")
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if "error" in data:
            print(f"[ERROR] API Error: {data.get('error')}")
        else:
            print("\n[SUCCESS] New Access Token Generated Automatically!")
            print(f"Access Token: {data.get('access_token')}")
            print(f"Expires in: {data.get('expires_in')} seconds")
            
    except Exception as e:
        print(f"[ERROR] Failed to refresh token: {e}")

if __name__ == "__main__":
    while True:
        refresh_access_token()
        print("[INFO] Waiting 5 seconds before next check (demo mode)...")
        time.sleep(5)
