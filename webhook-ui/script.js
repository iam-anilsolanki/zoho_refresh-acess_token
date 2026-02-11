document.addEventListener('DOMContentLoaded', () => {
    // === Auth State & Logic ===
    const authOverlay = document.getElementById('authOverlay');
    const authForm = document.getElementById('authForm');
    const authTitle = document.getElementById('authTitle');
    const authSubtitle = document.getElementById('authSubtitle');
    const submitBtn = document.getElementById('authSubmitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner');

    // Fields
    const nameGroup = document.getElementById('nameGroup');
    const passwordGroup = document.getElementById('passwordGroup');
    const authName = document.getElementById('authName');
    const authEmail = document.getElementById('authEmail');
    const authPassword = document.getElementById('authPassword');

    // Footer Sections
    const signInFooter = document.getElementById('signInFooter');
    const signUpFooter = document.getElementById('signUpFooter');
    const forgotFooter = document.getElementById('forgotFooter');

    let currentMode = 'signin'; // signin | signup | forgot

    // Session Check
    if (sessionStorage.getItem('auth_token')) {
        authOverlay.classList.add('hidden');
    }

    // Switch Mode Logic
    function setMode(mode) {
        currentMode = mode;
        // Reset warnings
        authEmail.style.borderColor = '';
        authPassword.style.borderColor = '';

        if (mode === 'signin') {
            authTitle.innerText = 'Welcome Back';
            authSubtitle.innerText = 'Enter your credentials to access.';
            btnText.innerText = 'Sign In';

            nameGroup.classList.add('hidden');
            passwordGroup.classList.remove('hidden');
            authPassword.required = true;
            authName.required = false;

            signInFooter.classList.remove('hidden');
            signUpFooter.classList.add('hidden');
            forgotFooter.classList.add('hidden');
        } else if (mode === 'signup') {
            authTitle.innerText = 'Create Account';
            authSubtitle.innerText = 'Join to start integrating workflows.';
            btnText.innerText = 'Sign Up';

            nameGroup.classList.remove('hidden');
            passwordGroup.classList.remove('hidden');
            authPassword.required = true;
            authName.required = true;

            signInFooter.classList.add('hidden');
            signUpFooter.classList.remove('hidden');
            forgotFooter.classList.add('hidden');
        } else if (mode === 'forgot') {
            authTitle.innerText = 'Reset Password';
            authSubtitle.innerText = 'We will send you a new password.';
            btnText.innerText = 'Reset Password';

            nameGroup.classList.add('hidden');
            passwordGroup.classList.add('hidden');
            authPassword.required = false;
            authName.required = false;

            signInFooter.classList.add('hidden');
            signUpFooter.classList.add('hidden');
            forgotFooter.classList.remove('hidden');
        }
    }

    // Event Listeners for switching
    document.getElementById('toSignUp').addEventListener('click', (e) => { e.preventDefault(); setMode('signup'); });
    document.getElementById('toForgot').addEventListener('click', (e) => { e.preventDefault(); setMode('forgot'); });
    document.getElementById('toSignInFromUp').addEventListener('click', (e) => { e.preventDefault(); setMode('signin'); });
    document.getElementById('toSignInFromForgot').addEventListener('click', (e) => { e.preventDefault(); setMode('signin'); });

    // Auth API Call
    async function callAuthApi(payload) {
        try {
            const response = await fetch('https://n8n.youngerslife.com/webhook/n8n/auth', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            return await response.json();
        } catch (error) {
            console.error('Auth Error:', error);
            return { status: 'error', message: 'Network connection failed' };
        }
    }

    function setAuthLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.classList.add('hidden');
            spinner.classList.remove('hidden');
        } else {
            submitBtn.disabled = false;
            btnText.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    }

    // Handle Auth Submit
    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        setAuthLoading(true);

        const email = authEmail.value;
        const password = authPassword.value;
        const name = authName.value;

        const payload = {
            path: currentMode,
            email: email
        };

        if (currentMode !== 'forgot') {
            payload.password = password;
        }
        if (currentMode === 'signup') {
            payload.name = name;
        }

        const result = await callAuthApi(payload);
        console.log('Auth Response:', result); // Debug log
        setAuthLoading(false);

        if (result.status === 'success' || result.isPasswordMatch === 1 || result.id || result.message === 'User registered successfully' || result.message === 'Login successful') {
            if (currentMode === 'signin' || currentMode === 'signup') {
                sessionStorage.setItem('auth_token', result.id || 'true'); // Use ID as token if available
                showToast('Welcome back!', 'success');
                authOverlay.classList.add('hidden');
                // Reset form
                authForm.reset();
            } else if (currentMode === 'forgot') {
                showToast('Password reset. Check your email/response.', 'success');
                // Optionally show the new password if API returns it directly for demo
                if (result.message) alert(result.message);
                setMode('signin');
            }
        } else {
            showToast(result.message || 'Authentication failed', 'error');
            if (currentMode !== 'forgot') authPassword.value = '';
        }
    });

    // === Webhook Logic ===
    const form = document.getElementById('webhookForm');
    const webhookSubmitBtn = document.getElementById('submitBtn');
    const webhookBtnText = webhookSubmitBtn.querySelector('.btn-text');
    const webhookSpinner = webhookSubmitBtn.querySelector('.spinner');

    function setLoading(isLoading) {
        if (isLoading) {
            webhookSubmitBtn.disabled = true;
            webhookBtnText.classList.add('hidden');
            webhookSpinner.classList.remove('hidden');
        } else {
            webhookSubmitBtn.disabled = false;
            webhookBtnText.classList.remove('hidden');
            webhookSpinner.classList.add('hidden');
        }
    }

    function showToast(message, type = 'success') {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        let icon = type === 'success'
            ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
            : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';

        toast.innerHTML = `${icon}<span>${message}</span>`;
        container.appendChild(toast);

        // Trigger animation
        requestAnimationFrame(() => toast.classList.add('show'));

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 400);
        }, 3000);
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        setLoading(true);

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const webhookUrl = data.webhookUrl;

        try {
            const response = await fetch(webhookUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                showToast('Payload transmitted successfully', 'success');
                form.reset();
            } else {
                throw new Error('Server returned ' + response.status);
            }
        } catch (error) {
            console.error('Submission Error:', error);
            showToast('Connection failed: ' + error.message, 'error');
        } finally {
            setLoading(false);
        }
    });

    // Make togglePassword available globally
    window.togglePassword = function (fieldId) {
        const input = document.getElementById(fieldId);
        if (input.type === 'password') {
            input.type = 'text';
        } else {
            input.type = 'password';
        }
    };

    // Logout Logic
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            sessionStorage.removeItem('auth_token');
            // Clear inputs
            document.getElementById('authEmail').value = '';
            document.getElementById('authPassword').value = '';
            authOverlay.classList.remove('hidden');
            setMode('signin');
            showToast('Logged out successfully', 'success');
        });
    }
});
