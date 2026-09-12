(function (djq) {
    'use strict';

    function mask(v) {
        var d = v.replace(/\D/g, '').slice(0, 12);
        if (!d) return '';
        var p = [];
        for (var i = 0; i < d.length; i += 3) p.push(d.substr(i, 3));
        return p.join('.');
    }

    function getJQ() {
        return window.jQuery || window.$ || djq;
    }

    function refreshSelect2(el) {
        if (!el) return;
        var $ = getJQ();
        if (!$.fn || !$.fn.select2) return;
        try {
            if ($(el).data('select2')) $(el).select2('destroy');
            $(el).select2({ width: '100%' });
        } catch (e) {
            if (console) console.warn('select2 error', e);
        }
    }

    function populate(el, items) {
        var html = '<option value="">---</option>';
        if (items && items.length) {
            for (var i = 0; i < items.length; i++) {
                var id = String(items[i].id).replace(/"/g, '&quot;');
                var txt = String(items[i].text)
                    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
                html += '<option value="' + id + '">' + txt + '</option>';
            }
        }
        el.innerHTML = html;
        el.value = '';
        var $ = getJQ();
        $(el).trigger('change');
        refreshSelect2(el);
    }

    function ajaxLoad(url, params, el) {
        if (!url) {
            populate(el, null);
            return;
        }
        var qs = Object.keys(params).map(function (k) {
            return encodeURIComponent(k) + '=' + encodeURIComponent(params[k]);
        }).join('&');
        var fullUrl = url + (qs ? '?' + qs : '');
        fetch(fullUrl, { credentials: 'same-origin' })
            .then(function (r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            }).then(function (resp) {
                var items = (resp && resp.results) ? resp.results : [];
                populate(el, items);
            }).catch(function () {
                populate(el, null);
            });
    }

    djq(document).on('input', '.mask-chart-account-code', function () {
        this.value = mask(this.value);
    });

    djq(document).ready(function () {
        var tipoConta = document.getElementById('id_account_type');
        var classeContabil = document.getElementById('id_account_class');
        var grupoPrincipal = document.getElementById('id_account_group');
        var subgrupo = document.getElementById('id_account_subgroup');

        if (!tipoConta) return;

        function loadClasses(typeId) {
            var url = tipoConta.getAttribute('data-classes-url') || '/administrative/ajax/filter-classes/';
            populate(classeContabil, null);
            populate(grupoPrincipal, null);
            populate(subgrupo, null);
            if (!typeId) { classeContabil.disabled = false; return; }
            ajaxLoad(url, { tipo_conta_id: typeId }, classeContabil);
        }

        function loadGroups(classId) {
            var url = (classeContabil ? classeContabil.getAttribute('data-groups-url') : null) || '/administrative/ajax/filter-groups/';
            populate(grupoPrincipal, null);
            populate(subgrupo, null);
            if (!classId) { grupoPrincipal.disabled = false; return; }
            ajaxLoad(url, { classe_contabil_id: classId }, grupoPrincipal);
        }

        function loadSubgroups(groupId) {
            var url = (grupoPrincipal ? grupoPrincipal.getAttribute('data-subgroups-url') : null) || '/administrative/ajax/filter-subgroups/';
            populate(subgrupo, null);
            if (!groupId) { subgrupo.disabled = false; return; }
            ajaxLoad(url, { grupo_principal_id: groupId }, subgrupo);
        }

        var $ = getJQ();
        $(tipoConta).on('change', function () {
            loadClasses(this.value);
        });
        $(classeContabil).on('change', function () {
            loadGroups(this.value);
        });
        $(grupoPrincipal).on('change', function () {
            loadSubgroups(this.value);
        });

        document.querySelectorAll('.mask-chart-account-code').forEach(function (el) {
            el.value = mask(el.value);
        });

        if (tipoConta.value) {
            classeContabil.disabled = false;
            if (classeContabil && classeContabil.value) {
                grupoPrincipal.disabled = false;
                if (subgrupo && subgrupo.value) {
                    subgrupo.disabled = false;
                }
            }
        }
    });

})(django.jQuery);
