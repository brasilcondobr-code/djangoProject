document.addEventListener('DOMContentLoaded', function() {
    const subjectField = document.querySelector('.mask-subject');
    const emailField = document.querySelector('.mask-email');
    const textFields = document.querySelectorAll('.mask-text');
    const attachmentsField = document.querySelector('input[type="file"]');

    if (emailField) {
        emailField.addEventListener('blur', function(e) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (this.value && !emailRegex.test(this.value)) {
                alert('Por favor, insira um e-mail válido.');
                this.focus();
            }
        });
    }

    // Exemplo de visualização de anexo (apenas nome do arquivo)
    if (attachmentsField) {
        attachmentsField.addEventListener('change', function(e) {
            if (this.files.length > 0) {
                console.log('Arquivo selecionado:', this.files[0].name);
            }
        });
    }
});
