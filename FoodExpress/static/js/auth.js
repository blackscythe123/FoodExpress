// Authentication related functionality

document.addEventListener('DOMContentLoaded', function() {
    // Form validation for registration
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            if (password !== confirmPassword) {
                e.preventDefault();
                
                const errorAlert = document.createElement('div');
                errorAlert.className = 'alert alert-danger';
                errorAlert.textContent = 'Passwords do not match!';
                
                // Remove any existing error alert
                const existingAlert = document.querySelector('.alert-danger');
                if (existingAlert) {
                    existingAlert.remove();
                }
                
                // Insert error alert at the top of the form
                registerForm.insertBefore(errorAlert, registerForm.firstChild);
                
                // Highlight the password fields
                document.getElementById('password').classList.add('is-invalid');
                document.getElementById('confirm_password').classList.add('is-invalid');
            }
        });
        
        // Live password strength indicator
        const passwordInput = document.getElementById('password');
        const strengthIndicator = document.getElementById('password-strength');
        
        if (passwordInput && strengthIndicator) {
            passwordInput.addEventListener('input', function() {
                const password = this.value;
                let strength = 0;
                
                if (password.length >= 8) strength += 1;
                if (password.match(/[a-z]/)) strength += 1;
                if (password.match(/[A-Z]/)) strength += 1;
                if (password.match(/[0-9]/)) strength += 1;
                if (password.match(/[^a-zA-Z0-9]/)) strength += 1;
                
                let strengthText = '';
                let strengthClass = '';
                
                switch (strength) {
                    case 0:
                    case 1:
                        strengthText = 'Weak';
                        strengthClass = 'text-danger';
                        break;
                    case 2:
                    case 3:
                        strengthText = 'Medium';
                        strengthClass = 'text-warning';
                        break;
                    case 4:
                    case 5:
                        strengthText = 'Strong';
                        strengthClass = 'text-success';
                        break;
                }
                
                strengthIndicator.textContent = `Password strength: ${strengthText}`;
                strengthIndicator.className = strengthClass;
            });
        }
    }
    
    // Clear form validation styling on input
    const formInputs = document.querySelectorAll('.form-control.is-invalid');
    formInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
        });
    });
    
    // Login form remember me toggle
    const rememberCheckbox = document.getElementById('remember');
    if (rememberCheckbox) {
        rememberCheckbox.addEventListener('change', function() {
            const label = document.querySelector('label[for="remember"]');
            if (this.checked) {
                label.classList.add('text-primary');
            } else {
                label.classList.remove('text-primary');
            }
        });
    }
});
