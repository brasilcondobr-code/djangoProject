document.addEventListener('DOMContentLoaded', function() {
    const smtpPortField = document.querySelector('.mask-smtp_port');
    const emailField = document.querySelector('.mask-email');
    const urlField = document.querySelector('.mask-api_url');
    
    const useTLSField = document.querySelector('input[name="use_tls"]');
    const useSSLField = document.querySelector('input[name="use_ssl"]');
    const smtpAuthField = document.querySelector('select[name="smtp_authentication"]');
    const usernameField = document.querySelector('.mask-username');
    const passwordField = document.querySelector('.mask-password');
    const timeoutField = document.querySelector('.mask-number'); // This is ambiguous, there are many mask-number fields.

    // Refined selection for timeout field based on label if possible, 
    // but since we don't have easy access to labels in pure JS without more DOM traversal, 
    // let's assume the user might have added a specific class or we find it by context.
    // Actually, in forms.py:
    // 'emails_per_hour': forms.NumberInput(attrs={'class': 'mask-number'}),
    // 'emails_per_day': forms.NumberInput(attrs={'class': 'mask-number'}),
    // 'max_recipients_per_email': forms.NumberInput(attrs={'class': 'mask-number'}),
    // 'last_test_duration': forms.NumberInput(attrs={'class': 'mask-number', 'placeholder': 'Tempo em segundos'}),
    // Let's look for the one with placeholder 'Tempo em segundos' if it was in the form, 
    // but it's not in the form for SMTPConfiguration, it's in the admin fieldsets.

    if (smtpPortField) {
        smtpPortField.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }

    if (emailField) {
        emailField.addEventListener('blur', function(e) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (this.value && !emailRegex.test(this.value)) {
                alert('Por favor, insira um e-mail válido.');
                this.focus();
            }
        });
    }

    if (urlField) {
        urlField.addEventListener('blur', function(e) {
            try {
                new URL(this.value);
            } catch (_) {
                if (this.value) {
                    alert('Por favor, insira uma URL válida.');
                    this.focus();
                }
            }
        });
    }

    // TLS/SSL mutual exclusion
    if (useTLSField && useSSLField) {
        useTLSField.addEventListener('change', function() {
            if (this.checked) {
                useSSLField.checked = false;
            }
        });
        useSSLField.addEventListener('change', function() {
            if (this.checked) {
                useTLSField.checked = false;
            }
        });
    }

    // Show/Hide Username and Password
    if (smtpAuthField && usernameField && passwordField) {
        const toggleAuthFields = () => {
            const isAuthRequired = smtpAuthField.value === 'True' || smtpAuthField.value === 'on' || smtpAuthField.value === 'Sim';
            // Django Select for BooleanField usually uses "True"/"False" or "on"
            // Let's check the actual value if possible.
            
            const show = (smtpAuthField.value === 'True' || smtpAuthField.value === 'Sim' || smtpAuthField.value === '1');
            
            const containers = [usernameField.closest('p'), passwordField.closest('p')];
            containers.forEach(container => {
                if (container) {
                    container.style.display = show ? 'block' : 'none';
                }
            });
        };

        smtpAuthField.addEventListener('change', toggleAuthFields);
        toggleAuthFields(); // Initial call
    }
});
