/**
 * BrasilCondo Utilities - Centralized Masks and Helper Functions
 * Goal: Reuse, Standardization, and Clean Architecture.
 */
const BrasilCondoUtils = {
    masks: {
        cpf: function(v) {
            v = v.replace(/\D/g, '');
            if (v.length <= 3) return v;
            if (v.length <= 6) return v.replace(/(\d{3})(\d+)/, '$1.$2');
            if (v.length <= 9) return v.replace(/(\d{3})(\d{3})(\d+)/, '$1.$2.$3');
            return v.replace(/(\d{3})(\d{3})(\d{3})(\d{3})/, '$1.$2.$3-$4').slice(0, 14);
        },
        cnpj: function(v) {
            v = v.replace(/\D/g, '');
            if (v.length <= 2) return v;
            if (v.length <= 5) return v.replace(/(\d{2})(\d+)/, '$1.$2');
            if (v.length <= 8) return v.replace(/(\d{2})(\d{3})(\d+)/, '$1.$2.$3');
            if (v.length <= 12) return v.replace(/(\d{2})(\d{3})(\d{3})(\d+)/, '$1.$2.$3/$4');
            return v.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{4})/, '$1.$2.$3/$4-$5').slice(0, 18);
        },
        phone: function(v) {
            v = v.replace(/\D/g, '');
            if (v.length <= 2) return v;
            if (v.length <= 6) return v.replace(/(\d{2})(\d+)/, '($1) $2');
            if (v.length <= 10) return v.replace(/(\d{2})(\d{4})(\d+)/, '($1) $2-$3');
            return v.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3').slice(0, 15);
        },
        date: function(v) {
            v = v.replace(/\D/g, '');
            if (v.length <= 2) return v;
            if (v.length <= 4) return v.replace(/(\d{2})(\d+)/, '$1/$2');
            return v.replace(/(\d{2})(\d{2})(\d{4})/, '$1/$2/$3').slice(0, 10);
        },
        email: function(v) {
            return v.replace(/[^a-zA-Z0-9@._-]/g, '');
        },
        decimal: function(v) {
            v = v.replace(/\D/g, '');
            if (v.length === 0) return '';
            var amount = (parseInt(v) / 100).toFixed(2).replace(".", ",");
            amount = amount.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
            return amount;
        }
    },
    
    applyMask: function(selector, maskType) {
        const maskFn = this.masks[maskType];
        if (!maskFn) {
            console.error(`Mask type ${maskType} not found in BrasilCondoUtils.`);
            return;
        }
        
        const $el = $(selector);
        $el.on('input', function() {
            $(this).val(maskFn($(this).val()));
        });
        
        // Initial application for existing values
        $el.each(function() {
            $(this).val(maskFn($(this).val()));
        });
    }
};
