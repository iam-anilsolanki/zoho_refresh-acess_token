import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_access_token():
    """
    Fetches a new Access Token from Zoho using the Refresh Token stored in .env.
    Returns the access token string if successful, or None if failed.
    """
    refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
    client_id = os.getenv("ZOHO_CLIENT_ID")
    client_secret = os.getenv("ZOHO_CLIENT_SECRET")
    accounts_url = os.getenv("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.com")

    if not all([refresh_token, client_id, client_secret]):
        print("[ERROR] Missing credentials in .env file.")
        print("Ensure ZOHO_REFRESH_TOKEN, ZOHO_CLIENT_ID, and ZOHO_CLIENT_SECRET are set.")
        return None

    url = f"{accounts_url}/oauth/v2/token"
    params = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }

    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if "error" in data:
            print(f"[ERROR] Zoho API Error: {data.get('error')}")
            return None
            
        access_token = data.get("access_token")
        expires_in = data.get("expires_in")
        
        print(f"[SUCCESS] Access Token Retrieved")
        print(f"Token: {access_token}")
        print(f"Expires in: {expires_in} seconds")
        
        return access_token

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] HTTP Request failed: {e}")
        return None

if __name__ == "__main__":
    get_access_token()
