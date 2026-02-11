# Zoho Refresh Token Automation

This project provides a set of tools to automate the process of obtaining and refreshing Zoho OAuth 2.0 tokens. It includes a user-friendly Web UI for the initial authentication flow and scripts for automatic token refreshing.

## Features

- **Interactive Web UI**: A clean, modern interface to initiate the OAuth flow and capture credentials.
- **Automated Token Capture**: Automatically handles the OAuth callback, exchanges the authorization code for tokens, and saves them.
- **Environment Management**: Automatically updates your `.env` file with the new Refresh Token.
- **Auto-Refresh Daemon**: A script to continuously refresh the Access Token in the background.
- **CLI/Script Support**: Includes standalone Python scripts for non-UI based token retrieval.

## Prerequisites

- **Python 3.7+**
- A **Zoho Account**
- A registered **Zoho Client** (Self Client or Server-based) with:
    - Client ID
    - Client Secret
    - Redirect URI (default: `http://localhost:8000/callback`)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd zoho_refresh_url
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Create a `.env` file in the root directory. You can use the provided `sample_env.txt` as a template:

    ```bash
    cp sample_env.txt .env
    ```

2.  Fill in your Zoho credentials in the `.env` file:

    ```ini
    ZOHO_CLIENT_ID=your_client_id_here
    ZOHO_CLIENT_SECRET=your_client_secret_here
    ZOHO_REDIRECT_URI=http://localhost:8000/callback
    ZOHO_SCOPES=ZohoProjects.projects.ALL,ZohoProjects.portals.ALL,ZohoProjects.tasks.ALL
    ZOHO_ACCOUNTS_URL=https://accounts.zoho.com
    # ZOHO_REFRESH_TOKEN will be populated automatically by the app
    ```

    > **Note:** The `ZOHO_REDIRECT_URI` must match exactly what you configured in the Zoho Developer Console. The port specified here (e.g., `8000`) will be used to run the local server.

## Usage

### Method 1: Using the Web UI (Recommended)

This method spins up a local Flask server with a nice UI to handle the authentication.

1.  **Start the Server:**
    ```bash
    python server.py
    ```
    You should see: `Starting Webhook UI Server on port 8000...`

2.  **Open the UI:**
    Go to `http://localhost:8000` in your browser.

3.  **Authenticate:**
    - Enter your **Client ID** and **Client Secret** (if not already loaded from `.env`).
    - Click **Start Automated Flow**.
    - You will be redirected to Zoho to approve the app.

4.  **Success:**
    - The server captures the code, exchanges it for a **Refresh Token**, and **automatically saves it to your `.env` file**.
    - The UI will display the new Refresh Token.

### Method 2: Using the CLI Script

If you prefer a command-line approach without the full UI:

1.  **Run the script:**
    ```bash
    python get_tokens.py
    ```

2.  **Follow the prompts:**
    - The script will automatically open your default browser to the Zoho consent page.
    - Login and accept.
    - The script listens for the callback, captures the token, and updates `.env`.

### Refreshing Access Tokens

Once you have a valid `ZOHO_REFRESH_TOKEN` in your `.env` file, you can generate Access Tokens.

**One-time Fetch:**
```bash
python get_access_token.py
```
*Prints the new Access Token and its expiry to the console.*

**Continuous Auto-Refresh (Daemon):**
```bash
python auto_refresh.py
```
*Runs in a loop, refreshing the token and printing the new one. Useful for testing or keeping a session alive during development.*

## Project Structure

- `server.py`: The main Flask application that serves the UI and handles the OAuth callback.
- `webhook-ui/`: Contains the HTML/CSS/JS for the frontend interface.
- `get_tokens.py`: A standalone script to get tokens using Python's `http.server`.
- `get_access_token.py`: Helper script to exchange a Refresh Token for an Access Token.
- `auto_refresh.py`: Demonstration script that refreshes the token in a loop.
