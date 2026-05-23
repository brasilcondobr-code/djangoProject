document.addEventListener('DOMContentLoaded', function() {
    const smtpPortField = document.querySelector('.mask-smtp_port');
    const emailField = document.querySelector('.mask-email');
    const urlField = document.querySelector('.mask-api_url');

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
});
