(function($){
  function maskCNPJ(v){
    v = v.replace(/\D/g, ''); // apenas dígitos
    v = v.substring(0, 14);
    if (v.length <= 2) return v;
    if (v.length <= 5) return v.replace(/(\d{2})(\d+)/, '$1.$2');
    if (v.length <= 8) return v.replace(/(\d{2})(\d{3})(\d+)/, '$1.$2.$3');
    if (v.length <= 12) return v.replace(/(\d{2})(\d{3})(\d{3})(\d+)/, '$1.$2.$3/$4');
    return v.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{0,2})/, '$1.$2.$3/$4-$5');
  }

  $(document).ready(function(){

    console.log('O arquivo custom-admin-realestateagency.js está carregado');

    if ($().jquery) {
        console.log('O jQuery está carregado corretamente');
    } else {
        console.log('O jQuery não está sendo carregado corretamente');
    }

    django.jQuery('.mask-cnpj').on('input', function(){
      this.value = maskCNPJ(this.value);
    });

    django.jQuery('.mask-email').on('input', function(){
      this.value = this.value.replace(/[^a-zA-Z0-9@._-]/g, '');
    });

    django.jQuery('.mask-phone').on('input', function(){
      var phone = this.value.replace(/\D/g, '');
      phone = phone.replace(/(\d{2})(\d)/, '($1) $2');
      phone = phone.replace(/(\d{4,5})(\d{4})$/, '$1-$2');
      this.value = phone;
    });

    django.jQuery('.mask-website').on('input', function(){
      this.value = this.value.replace(/[^a-zA-Z0-9.-]/g, '');
    });

  });
  
})(django.jQuery);