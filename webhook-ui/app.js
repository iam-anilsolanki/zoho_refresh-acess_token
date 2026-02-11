document.getElementById('authForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = document.getElementById('submitBtn');
    const status = document.getElementById('status');
    const statusMessage = document.getElementById('statusMessage');

    const clientId = document.getElementById('clientId').value;
    const clientSecret = document.getElementById('clientSecret').value;

    // UI Feedback
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;
    status.classList.remove('hidden');
    statusMessage.innerText = "Initiating OAuth flow...";

    try {
        const response = await fetch('/api/initiate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ clientId, clientSecret })
        });

        const data = await response.json();

        if (data.authUrl) {
            statusMessage.innerText = "Redirecting to Zoho for permission...";
            // Redirect the user to Zoho
            window.location.href = data.authUrl;
        } else {
            throw new Error('No Auth URL returned');
        }

    } catch (error) {
        console.error('Error:', error);
        statusMessage.innerText = "Error: " + error.message;
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
    }
});

// If we are on the result page (checking by presence of refreshTokenDisplay which handles the display logic if pre-filled)
document.addEventListener('DOMContentLoaded', () => {
    // Check URL params for token (simplest way to pass back from backend redirect)
    const urlParams = new URLSearchParams(window.location.search);
    const refreshToken = urlParams.get('refresh_token');

    if (refreshToken) {
        document.querySelector('.container').innerHTML = `
           <div id="result" class="result-box">
            <h3>Refresh Token Retrieved!</h3>
            <div class="token-container">
                <code id="refreshTokenDisplay">${refreshToken}</code>
                <button id="copyBtn">Copy</button>
            </div>
            <p class="warning">Keep this token secure. Do not share it.</p>
             <a href="/" style="display:block; margin-top:20px; text-align:center;">Back to Home</a>
        </div>
       `;

        document.getElementById('copyBtn').addEventListener('click', () => {
            navigator.clipboard.writeText(refreshToken);
            const btn = document.getElementById('copyBtn');
            const originalText = btn.innerText;
            btn.innerText = "Copied!";
            setTimeout(() => {
                btn.innerText = originalText;
            }, 2000);
        });
    }
});
