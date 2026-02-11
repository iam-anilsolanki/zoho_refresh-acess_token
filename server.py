from flask import Flask, request, redirect, jsonify, send_from_directory
import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load configured scope
load_dotenv()
DEFAULT_SCOPES = os.getenv("ZOHO_SCOPES", "ZohoProjects.projects.ALL")
ACCOUNTS_URL = os.getenv("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.com")

# STRICT: Always get redirect URI from env. Fail if missing.
REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI")
if not REDIRECT_URI:
    raise ValueError("ZOHO_REDIRECT_URI must be set in .env")

# Parse REDIRECT_URI for server configuration
parsed_uri = urlparse(REDIRECT_URI)
SERVER_PORT = parsed_uri.port
if not SERVER_PORT:
     raise ValueError("ZOHO_REDIRECT_URI must include a port (e.g., http://localhost:8000/callback)")
CALLBACK_PATH = parsed_uri.path or "/"

app = Flask(__name__, static_folder='webhook-ui')

# Store temp cache for dynamic credentials
# Key: client_id, Value: client_secret
app.config['CLIENT_SECRETS'] = {}

@app.route('/')
def home():
    return send_from_directory('webhook-ui', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('webhook-ui', path)

@app.route('/api/initiate', methods=['POST'])
def initiate_auth():
    data = request.json
    client_id = data.get('clientId')
    client_secret = data.get('clientSecret')

    if not client_id or not client_secret:
        return jsonify({'error': 'Missing credentials'}), 400

    # Store secret for the callback
    app.config['CLIENT_SECRETS'][client_id] = client_secret

    # Construct Zoho URL
    params = {
        "scope": DEFAULT_SCOPES,
        "client_id": client_id,
        "response_type": "code",
        "access_type": "offline",
        "redirect_uri": REDIRECT_URI,
        "prompt": "consent"
    }
    
    auth_req = requests.Request('GET', f"{ACCOUNTS_URL}/oauth/v2/auth", params=params)
    auth_url = auth_req.prepare().url
    
    return jsonify({'authUrl': auth_url})

# Dynamic callback route registration happens below
def callback():
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        return f"<h1>Error: {error}</h1>"
    
    if not code:
        return "<h1>Error: No code received</h1>"

    if not app.config['CLIENT_SECRETS']:
        return "<h1>Error: No pending authentication found in server memory.</h1>"
    
    # Get the most recent one
    client_id, client_secret = list(app.config['CLIENT_SECRETS'].items())[-1]

    # Exchange token
    url = f"{ACCOUNTS_URL}/oauth/v2/token"
    params = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }

    try:
        response = requests.post(url, params=params)
        tokens = response.json()
        
        if "error" in tokens:
            return f"<h1>Zoho API Error: {tokens.get('error')}</h1>"
            
        refresh_token = tokens.get('refresh_token')
        
        # Save Refresh Token to .env
        try:
            env_path = os.path.join(os.path.dirname(__file__), '.env')
            new_lines = []
            token_saved = False
            
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith("ZOHO_REFRESH_TOKEN="):
                            new_lines.append(f"ZOHO_REFRESH_TOKEN={refresh_token}\n")
                            token_saved = True
                        else:
                            new_lines.append(line)
            
            if not token_saved:
                if len(new_lines) > 0 and not new_lines[-1].endswith('\n'):
                    new_lines.append('\n')
                new_lines.append(f"ZOHO_REFRESH_TOKEN={refresh_token}\n")
            
            with open(env_path, "w") as f:
                f.writelines(new_lines)
                
            print(f"[INFO] Saved Refresh Token to {env_path}")
            
        except Exception as save_error:
            print(f"[ERROR] Could not save to .env: {save_error}")

        return redirect(f"/?refresh_token={refresh_token}")
        
    except Exception as e:
        return f"<h1>Server Error: {str(e)}</h1>"

# Register the callback route dynamically based on env var path
app.add_url_rule(CALLBACK_PATH, 'callback', callback)

if __name__ == '__main__':
    print(f"Starting Webhook UI Server on port {SERVER_PORT} (Callback Path: {CALLBACK_PATH})...")
    app.run(port=SERVER_PORT, debug=True)
