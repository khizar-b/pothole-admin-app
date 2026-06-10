// Login Form Handler
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    const errorMessage = document.getElementById('errorMessage');
    
    // Check if already logged in
    const token = localStorage.getItem('token');
    if (token) {
        window.location.href = '/dashboard';
    }
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        // Disable button and show loading
        loginBtn.disabled = true;
        loginBtn.textContent = 'Logging in...';
        errorMessage.style.display = 'none';
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Store token and username
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('username', data.username);
                
                // Redirect to dashboard
                window.location.href = '/dashboard';
            } else {
                // Show error
                errorMessage.textContent = data.error || 'Login failed';
                errorMessage.style.display = 'block';
            }
        } catch (error) {
            errorMessage.textContent = 'Connection error. Please try again.';
            errorMessage.style.display = 'block';
        } finally {
            // Re-enable button
            loginBtn.disabled = false;
            loginBtn.textContent = 'Login';
        }
    });
    
    // Clear error on input
    document.getElementById('username').addEventListener('input', function() {
        errorMessage.style.display = 'none';
    });
    
    document.getElementById('password').addEventListener('input', function() {
        errorMessage.style.display = 'none';
    });
});
