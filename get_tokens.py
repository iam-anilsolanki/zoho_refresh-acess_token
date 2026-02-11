import os
import webbrowser
import requests
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")

# STRICT: Always get redirect URI from env. Fail if missing.
REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI")
if not REDIRECT_URI:
    raise ValueError("ZOHO_REDIRECT_URI must be set in .env")

SCOPES = os.getenv("ZOHO_SCOPES", "ZohoCRM.modules.ALL")
ACCOUNTS_URL = os.getenv("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.com")

# Global variable to store the captured code
grant_token = None
server_instance = None
stop_event = threading.Event()

# Parse the REDIRECT_URI to get path and port
parsed_redirect_uri = urlparse(REDIRECT_URI)
REDIRECT_PATH = parsed_redirect_uri.path if parsed_redirect_uri.path else "/"
REDIRECT_PORT = parsed_redirect_uri.port
if not REDIRECT_PORT:
     raise ValueError("ZOHO_REDIRECT_URI must include a port (e.g., http://localhost:8000/callback)")

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global grant_token
        parsed_url = urlparse(self.path)
        
        # Check if the requested path matches the configured redirect path
        if parsed_url.path == REDIRECT_PATH:
            query_params = parse_qs(parsed_url.query)
            
            if "code" in query_params:
                grant_token = query_params["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Success! You can close this window now.</h1>")
                print(f"\n[SUCCESS] Grant Token captured successfully.")
                stop_event.set()
            elif "error" in query_params:
                self.send_response(400)
                self.wfile.write(b"<h1>Error during authorization.</h1>")
                print(f"\n[ERROR] Authorization error: {query_params.get('error', ['Unknown'])[0]}")
                stop_event.set()
        else:
            self.send_response(404)
            self.end_headers()

def get_authorization_url():
    """Constructs the Zoho Authorization URL."""
    params = {
        "scope": SCOPES,
        "client_id": CLIENT_ID,
        "response_type": "code",
        "access_type": "offline",
        "redirect_uri": REDIRECT_URI,
        "prompt": "consent"
    }
    req = requests.Request('GET', f"{ACCOUNTS_URL}/oauth/v2/auth", params=params)
    return req.prepare().url

def exchange_code_for_tokens(code):
    """Exchanges the grant code for refresh and access tokens."""
    url = f"{ACCOUNTS_URL}/oauth/v2/token"
    params = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    
    print("\n[INFO] Exchanging Grant Token for Refresh Token...")
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        tokens = response.json()
        
        if "error" in tokens:
             print(f"\n[ERROR] API Error: {tokens.get('error')}")
             return

        print("\n" + "="*50)
        print(" ZOHO TOKENS RECEIVED")
        print("="*50)
        print(f"Refresh Token: {tokens.get('refresh_token')}")
        print(f"Access Token:  {tokens.get('access_token')}")
        print("="*50)
        
        # Save to .env
        env_path = ".env"
        new_lines = []
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if not line.startswith("ZOHO_REFRESH_TOKEN"):
                         new_lines.append(line)
        
        new_lines.append(f"ZOHO_REFRESH_TOKEN={tokens.get('refresh_token')}\n")
        
        with open(env_path, "w") as f:
            f.writelines(new_lines)

        print("[INFO] Refresh Token updated in .env file.")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to exchange token: {e}")
        if 'response' in locals():
             print(f"Response: {response.text}")

def run_server():
    """Starts the local server in a separate thread."""
    global server_instance
    server_address = ('', REDIRECT_PORT)
    server_instance = HTTPServer(server_address, OAuthCallbackHandler)
    # Set a timeout so handle_request doesn't block forever, allowing loop to check stop_event
    server_instance.timeout = 1 
    print(f"[INFO] Listening on {REDIRECT_URI} (Port: {REDIRECT_PORT}, Path: {REDIRECT_PATH})...")
    
    while not stop_event.is_set():
        server_instance.handle_request()

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET must be set in .env")
        return

    print("--- Zoho OAuth Automation ---")
    print(f"Using Client ID: {CLIENT_ID}")
    
    # 1. Start Server
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    
    # 2. Generate Auth URL
    auth_url = get_authorization_url()
    print(f"\n[STEP 1] Opening browser to: {auth_url}")
    
    # 3. Open Browser
    # Give server a moment to start
    time.sleep(1) 
    webbrowser.open(auth_url)
    
    print("[STEP 2] Waiting for you to login and accept...")
    
    try:
        # Wait for the token captured event (timeout after 5 minutes)
        if stop_event.wait(timeout=300):
            if grant_token:
               exchange_code_for_tokens(grant_token)
            else:
               print("[ERROR] Failed to get grant token.")
        else:
             print("[TIMEOUT] Timed out waiting for callback.")
             stop_event.set() # Ensure server loop stops
             
    except KeyboardInterrupt:
        print("\n[INFO] User interrupted.")
        stop_event.set()
    
    print("Exiting...")

if __name__ == "__main__":
    main()
