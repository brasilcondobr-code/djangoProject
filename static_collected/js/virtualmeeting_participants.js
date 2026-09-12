(function($) {
    'use strict';

    function initVirtualMeetingParticipants() {
        var $groups = $('#id_participating_groups');
        var $residents = $('#id_participating_resident');
        var $condominium = $('#id_condominium');

        if (!$groups.length || !$residents.length) {
            return;
        }

        var url = $groups.attr('data-participants-url') ||
            '/administrative/ajax/participants-by-group/';
        var controller = null;

        function currentGroupId() {
            var value = $groups.val();
            return value ? String(value) : '';
        }

        function currentCondominiumId() {
            return $condominium.length ? String($condominium.val() || '') : '';
        }

        function selectedResidentIds() {
            var value = $residents.val();
            if (Array.isArray(value)) {
                return value;
            }
            return value ? [value] : [];
        }

        function notifyChange($field) {
            var element = $field[0];
            if (element) {
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }
            $field.trigger('change');
        }

        function loadParticipants() {
            var groupId = currentGroupId();

            if (controller) {
                controller.abort();
            }
            controller = new AbortController();

            if (!groupId) {
                $residents.empty();
                $residents.prop('disabled', false);
                notifyChange($residents);
                return;
            }

            var previouslySelected = selectedResidentIds();
            var selected = {};
            previouslySelected.forEach(function(id) {
                selected[String(id)] = true;
            });

            $residents.prop('disabled', true);

            var params = new URLSearchParams();
            params.append('group_ids', groupId);
            var condominiumId = currentCondominiumId();
            if (condominiumId) {
                params.append('condominium_id', condominiumId);
            }

            fetch(url + '?' + params.toString(), {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                signal: controller.signal
            })
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status);
                    }
                    return response.json();
                })
                .then(function(data) {
                    var results = data.results || [];
                    var resultIds = {};
                    results.forEach(function(item) {
                        resultIds[String(item.id)] = true;
                    });

                    $residents.find('option').each(function() {
                        if (!resultIds[String(this.value)]) {
                            $(this).remove();
                        }
                    });

                    results.forEach(function(item) {
                        var id = String(item.id);
                        if (!$residents.find('option[value="' + id + '"]').length) {
                            $residents.append(new Option(item.text, id));
                        }
                    });

                    var toRestore = [];
                    results.forEach(function(item) {
                        if (selected[String(item.id)]) {
                            toRestore.push(String(item.id));
                        }
                    });
                    $residents.val(toRestore);
                    $residents.prop('disabled', false);
                    notifyChange($residents);
                })
                .catch(function(error) {
                    if (error.name === 'AbortError') {
                        return;
                    }
                    $residents.prop('disabled', false);
                    notifyChange($residents);
                });
        }

        function bindChangeEvent(element, handler) {
            if (!element) {
                return;
            }
            var timer = null;
            var changed = function() {
                clearTimeout(timer);
                timer = setTimeout(handler, 50);
            };
            var bound = [];
            var attach = function(jq) {
                if (!jq || typeof jq !== 'function' || !jq.fn || !jq.fn.on) {
                    return;
                }
                if (bound.indexOf(jq.fn) !== -1) {
                    return;
                }
                bound.push(jq.fn);
                try {
                    jq(element).on('change.virtual-meeting-participants', changed);
                } catch (e) {}
            };
            element.addEventListener('change', changed);
            attach($);
            attach(window.jQuery);
            attach(window.$);
        }

        bindChangeEvent($groups[0], loadParticipants);

        if ($condominium.length) {
            bindChangeEvent($condominium[0], loadParticipants);
        }

        loadParticipants();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVirtualMeetingParticipants);
    } else {
        initVirtualMeetingParticipants();
    }
})(django.jQuery || jQuery);