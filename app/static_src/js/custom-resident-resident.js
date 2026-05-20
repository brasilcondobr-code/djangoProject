(function($){
    $(function(){
        console.log('O arquivo custom-admin-resident.js está carregado');

        if ($().jquery) {
            console.log('O jQuery está carregado corretamente');
        } else {
            console.log('O jQuery não está sendo carregado corretamente');
        }

        $('.mask-email').on('input', function(){
            var email = $(this).val();

            // Aplica a máscara de email
            email = email.replace(/[^a-zA-Z0-9@._-]/g, ''); // Remove caracteres inválidos
            $(this).val(email);
        });

        $('.mask-phone').on('input', function(){
            var phone = $(this).val();
            // Remove tudo que não for número
            phone = phone.replace(/\D/g, '');
            // Aplica a máscara
            phone = phone.replace(/(\d{2})(\d)/, '($1) $2');
            phone = phone.replace(/(\d{4,5})(\d{4})$/, '$1-$2');
            $(this).val(phone);
        });

        $('.mask-date-of-birth').on('input', function(){
            var value = $(this).val();
            var digits = value.replace(/\D/g, '').slice(0, 8);
            if (digits.length <= 2) {
                $(this).val(digits);
                return;
            }
            if (digits.length <= 4) {
                $(this).val(digits.slice(0, 2) + '/' + digits.slice(2));
                return;
            }
            $(this).val(digits.slice(0, 2) + '/' + digits.slice(2, 4) + '/' + digits.slice(4));
        });

        // Atualiza quando qualquer um dos campos mudar
        $('.mask-cpf').on('input', function(){
            var cpf = $(this).val();
            // Remove tudo que não for número
            cpf = cpf.replace(/\D/g, '');
            // Aplica a máscara
            cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
            cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
            cpf = cpf.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
            $(this).val(cpf);
        });

        // Faz com que o link da foto abra em nova aba
        $('.field-photo a').attr('target', '_blank');
        
        // Faz com que o link do arquivo da certidão abra em nova aba
        $('.field-certificate_file a').attr('target', '_blank');

    });
})(django.jQuery);