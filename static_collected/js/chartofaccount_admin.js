(function($) {
    'use strict';

    function maskChartAccountCode(v) {
        var digits = v.replace(/\D/g, '');
        if (digits.length === 0) return '';
        digits = digits.slice(0, 12);
        var parts = [];
        for (var i = 0; i < digits.length; i += 3) {
            parts.push(digits.substr(i, 3));
        }
        return parts.join('.');
    }

    $(document).on('input', '.mask-chart-account-code', function() {
        $(this).val(maskChartAccountCode($(this).val()));
    });

    var xhrClasses = null;
    var xhrGroups = null;
    var xhrSubgroups = null;

    var _loadingClasses = false;
    var _loadingGroups = false;
    var _loadingSubgroups = false;

    function clearAndAddPlaceholder(sel) {
        $(sel).empty().append('<option value="">---------</option>');
        $(sel).trigger('change.select2');
    }

    function loadClasses(typeId) {
        if (xhrClasses && xhrClasses.readyState !== 4) xhrClasses.abort();
        _loadingClasses = true;

        clearAndAddPlaceholder('#id_account_class');
        clearAndAddPlaceholder('#id_account_group');
        clearAndAddPlaceholder('#id_account_subgroup');

        if (!typeId) {
            _loadingClasses = false;
            return;
        }

        var url = $('#id_account_type').data('classes-url');
        xhrClasses = $.getJSON(url, {type_id: typeId}, function(resp) {
            if (resp.results && resp.results.length) {
                $.each(resp.results, function(i, item) {
                    $('#id_account_class').append($('<option>', {value: item.id, text: item.text}));
                });
            }
            $('#id_account_class').trigger('change.select2');
        }).always(function() {
            _loadingClasses = false;
        });
    }

    function loadGroups(classId) {
        if (xhrGroups && xhrGroups.readyState !== 4) xhrGroups.abort();
        _loadingGroups = true;

        clearAndAddPlaceholder('#id_account_group');
        clearAndAddPlaceholder('#id_account_subgroup');

        if (!classId) {
            _loadingGroups = false;
            return;
        }

        var url = $('#id_account_class').data('groups-url');
        xhrGroups = $.getJSON(url, {class_id: classId}, function(resp) {
            if (resp.results && resp.results.length) {
                $.each(resp.results, function(i, item) {
                    $('#id_account_group').append($('<option>', {value: item.id, text: item.text}));
                });
            }
            $('#id_account_group').trigger('change.select2');
        }).always(function() {
            _loadingGroups = false;
        });
    }

    function loadSubgroups(groupId) {
        if (xhrSubgroups && xhrSubgroups.readyState !== 4) xhrSubgroups.abort();
        _loadingSubgroups = true;

        clearAndAddPlaceholder('#id_account_subgroup');

        if (!groupId) {
            _loadingSubgroups = false;
            return;
        }

        var url = $('#id_account_group').data('subgroups-url');
        xhrSubgroups = $.getJSON(url, {group_id: groupId}, function(resp) {
            if (resp.results && resp.results.length) {
                $.each(resp.results, function(i, item) {
                    $('#id_account_subgroup').append($('<option>', {value: item.id, text: item.text}));
                });
            }
            $('#id_account_subgroup').trigger('change.select2');
        }).always(function() {
            _loadingSubgroups = false;
        });
    }

    $(document).on('change', '#id_account_type', function() {
        if (_loadingClasses) return;
        loadClasses($('#id_account_type').val());
    });

    $(document).on('change', '#id_account_class', function() {
        if (_loadingGroups) return;
        loadGroups($('#id_account_class').val());
    });

    $(document).on('change', '#id_account_group', function() {
        if (_loadingSubgroups) return;
        loadSubgroups($('#id_account_group').val());
    });

    function initEditMode() {
        var typeId = $('#id_account_type').val();
        if (!typeId) return;
        var classId = $('#id_account_class').val();
        var groupId = $('#id_account_group').val();
        var subgroupId = $('#id_account_subgroup').val();

        _loadingClasses = true;
        _loadingGroups = true;
        _loadingSubgroups = true;

        var clearFlags = function() {
            _loadingClasses = false;
            _loadingGroups = false;
            _loadingSubgroups = false;
        };

        loadClasses(typeId);
        if (classId) {
            loadGroups(classId);
        }
        if (groupId) {
            loadSubgroups(groupId);
        }
        clearFlags();
    }

    $(document).ready(function() {
        $('.mask-chart-account-code').each(function() {
            $(this).val(maskChartAccountCode($(this).val()));
        });
        initEditMode();
    });

})(django.jQuery);
