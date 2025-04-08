document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Hide all tab contents
            tabContents.forEach(content => {
                content.style.display = 'none';
            });
            
            // Show the selected tab content
            const tabId = this.dataset.tab;
            document.getElementById(tabId + '-tab').style.display = 'block';
        });
    });
    
    // Student Login
    const loginBtn = document.getElementById('login-btn');
    const studentIdInput = document.getElementById('student-id');
    const studentErrorMessage = document.getElementById('student-error-message');
    
    loginBtn.addEventListener('click', function() {
        const studentId = studentIdInput.value.trim();
        
        if (!studentId) {
            studentErrorMessage.textContent = 'Please enter your Student ID';
            return;
        }
        
        // Clear previous error
        studentErrorMessage.textContent = '';
        
        // Send login request
        fetch('/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ student_id: studentId }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.redirect;
            } else {
                studentErrorMessage.textContent = data.message;
            }
        })
        .catch(error => {
            studentErrorMessage.textContent = 'An error occurred. Please try again.';
            console.error('Error:', error);
        });
    });
    
    // Admin Login
    const adminLoginBtn = document.getElementById('admin-login-btn');
    const adminUsernameInput = document.getElementById('admin-username');
    const adminPasswordInput = document.getElementById('admin-password');
    const adminErrorMessage = document.getElementById('admin-error-message');
    
    adminLoginBtn.addEventListener('click', function() {
        const username = adminUsernameInput.value.trim();
        const password = adminPasswordInput.value.trim();
        
        if (!username || !password) {
            adminErrorMessage.textContent = 'Please enter both username and password';
            return;
        }
        
        // Clear previous error
        adminErrorMessage.textContent = '';
        
        // Send admin login request
        fetch('/admin_login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: username, password: password }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.redirect;
            } else {
                adminErrorMessage.textContent = data.message;
            }
        })
        .catch(error => {
            adminErrorMessage.textContent = 'An error occurred. Please try again.';
            console.error('Error:', error);
        });
    });
    
    // Allow Enter key to submit
    studentIdInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            loginBtn.click();
        }
    });
    
    adminPasswordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            adminLoginBtn.click();
        }
    });
});