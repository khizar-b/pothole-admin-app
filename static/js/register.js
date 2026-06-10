// Registration functionality
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const email = document.getElementById('email').value.trim();
        
        // Validate passwords match
        if (password !== confirmPassword) {
            showError('Passwords do not match');
            return;
        }
        
        // Validate password length
        if (password.length < 6) {
            showError('Password must be at least 6 characters long');
            return;
        }
        
        // Validate username length
        if (username.length < 3) {
            showError('Username must be at least 3 characters long');
            return;
        }
        
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    email: email || null
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Registration successful, redirect to login
                alert('Registration successful! Please login with your credentials.');
                window.location.href = '/';
            } else {
                showError(data.error || 'Registration failed');
            }
        } catch (error) {
            showError('Registration error: ' + error.message);
        }
    });
    
    // Google Sign-In button
    window.onload = function () {
        google.accounts.id.initialize({
            client_id: 'YOUR_GOOGLE_CLIENT_ID_HERE', // Replace with actual Google Client ID
            callback: handleGoogleSignIn
        });
        
        // Only show button if Google API is properly configured
        const googleBtn = document.getElementById('googleSignInBtn');
        googleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            google.accounts.id.prompt();
        });
    };
});

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function handleGoogleSignIn(response) {
    // Send the token to your backend
    fetch('/api/auth/google-signin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: response.credential
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.access_token) {
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('username', data.username);
            window.location.href = '/dashboard';
        } else {
            showError(data.error || 'Google sign-in failed');
        }
    })
    .catch(error => {
        showError('Error during Google sign-in: ' + error.message);
    });
}
