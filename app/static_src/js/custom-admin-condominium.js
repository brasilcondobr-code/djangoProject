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

    console.log('O arquivo custom-admin-resident.js está carregado');

    if ($().jquery) {
        console.log('O jQuery está carregado corretamente');
    } else {
        console.log('O jQuery não está sendo carregado corretamente');
    }

    django.jQuery('.mask-code').on('input', function(){
      this.value = this.value.toUpperCase();
    });

    django.jQuery('.mask-cnpj').on('input', function(){
      this.value = maskCNPJ(this.value);
    });

  });
  
})(django.jQuery);