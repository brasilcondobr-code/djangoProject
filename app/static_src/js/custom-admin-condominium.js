/**
django.jQuery(function($) {
    console.log('O arquivo custom-admin-condominium.js está carregado');
    django.jQuery('head').load('/static_src/js/jquery.mask.min.js');

    if ($().jquery) {
        console.log('O jQuery está carregado corretamente');
    } else {
        console.log('O jQuery não está sendo carregado corretamente');
    }

    django.jQuery('.mask-cnpj').mask('00.000.000/0000-00', {reverse: true});
});
**/

// Máscara básica de CNPJ (99.999.999/9999-99)
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
    // tente pelo id padrão do field Django admin
    var el = $('#cnpj');
    if (!el.length) {
      // fallback comum: input com name='cnpj'
      el = $('input[name="cnpj"]');
    }
    if (!el.length) return;

    el.on('input', function(){
      var val = $(this).val();
      $(this).val(maskCNPJ(val));
    });

    if (el.val()) el.val(maskCNPJ(el.val()));
  });
})(jQuery);