(function($){
    $(document).ready(function(){
        function applyMasks() {
            $('.mask-chart-account-code').on('input', function(){
                var value = $(this).val().replace(/[^0-9]/g, '');
                var parts = [];
                for (var i = 0; i < value.length && i < 12; i += 3) {
                    parts.push(value.substr(i, 3));
                }
                $(this).val(parts.join('.'));
            });
        }
        applyMasks();
    });
})(django.jQuery);
