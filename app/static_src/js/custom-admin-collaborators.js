(function($){
  function maskCPF(v){
    v = v.replace(/\D/g, ''); // apenas dígitos
    v = v.substring(0, 11);
    if (v.length <= 3) return v;
    if (v.length <= 6) return v.replace(/(\d{3})(\d+)/, '$1.$2');
    if (v.length <= 9) return v.replace(/(\d{3})(\d{3})(\d+)/, '$1.$2.$3');
    return v.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, '$1.$2.$3-$4');
  }

  function maskPhone(v){
    v = v.replace(/\D/g, ''); // apenas dígitos
    v = v.substring(0, 11);
    if (v.length <= 2) return v;
    if (v.length <= 6) return v.replace(/(\d{2})(\d+)/, '($1) $2');
    return v.replace(/(\d{2})(\d{4,5})(\d{4})/, '($1) $2-$3');
  }

  $(document).ready(function(){

    django.jQuery('.mask-cpf').on('input', function(){
      this.value = maskCPF(this.value);
    });

    django.jQuery('.mask-email').on('input', function(){
      this.value = this.value.replace(/[^a-zA-Z0-9@._-]/g, '');
    });

    django.jQuery('.mask-phone').on('input', function(){
      this.value = maskPhone(this.value);
    });

  });
  
})(django.jQuery);