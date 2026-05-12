(function($){
    $(function(){
        console.log('O arquivo custom-admin-visitor.js está carregado');

        if ($().jquery) {
            console.log('O jQuery está carregado corretamente');
        } else {
            console.log('O jQuery não está sendo carregado corretamente');
        }

        $('.mask-phone').on('input', function(){
            var phone = $(this).val();
            // Remove tudo que não for número
            phone = phone.replace(/\D/g, '');
            // Aplica a máscara
            phone = phone.replace(/(\d{2})(\d)/, '($1) $2');
            phone = phone.replace(/(\d{4,5})(\d{4})$/, '$1-$2');
            $(this).val(phone);
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

    });
})(django.jQuery);