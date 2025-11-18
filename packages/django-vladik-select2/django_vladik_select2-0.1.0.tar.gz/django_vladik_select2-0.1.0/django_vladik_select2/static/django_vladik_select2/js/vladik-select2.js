window.VladikSelect = (function () {
    const events = { load: [] };
    function trigger(eventName, payload) {
        (events[eventName] || []).forEach(fn => fn(payload));
    }

    function init(scope = document) {
        scope.querySelectorAll("select[data-select]").forEach((select) => {
            const $select = $(select);
            if ($select.data('select2')) {
                $select.select2('destroy');
            }
            const type   = select.dataset.select;
            const model  = select.dataset.model;
            const depend = select.dataset.depend;
            const depSelect = depend ? scope.querySelector(`[name="${depend}"]`) : null;
            const url    = "/vladik-select2/api/";

            const baseConfig = {
                placeholder: "Seleccionar",
                width: "100%",
                minimumResultsForSearch: type === "simple" ? Infinity : 0,
                dropdownParent:  $(select).closest('.modal-content').length ? $(select).closest('.modal-content') : null
            };

            $select.select2(baseConfig);
            select.dataset.vladikSelectInit = "1";
            if (type === "search" || type === "source") {
                $select.on("select2:open", () => {
                    setTimeout(() => {
                        const input = document.querySelector(".select2-container--open .select2-search__field");
                        if (input) input.focus();
                    }, 0);
                });
            }

            function loadStatic() {
                if (depend && (!depSelect || !depSelect.value)) {
                    $select.empty().val(null).trigger("change");
                    return;
                }

                //const params = new URLSearchParams({ model });
                //if (type === "search") params.set("term", "");
                //if (depend && depSelect.value) params.set(`depend_${depend}`, depSelect.value);
                 const payload = {
                    model: model,
                    term: type === "search" ? "" : null,
                    depend: depend ? depSelect.value : null
                };

                //fetch(`${url}?${params}`)
                fetch(url, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload)
                    })
                    .then(r => r.json())
                    .then(data => {
                        $select.empty();
                        data.results.forEach(opt => {
                            $select.append(new Option(opt.text, opt.id));
                        });
                        $select.val(null).trigger("change");
                        trigger("load", select);
                    });
            }
            
            if (type === "source") {
                if ($select.data('select2')) {
                    $select.select2('destroy');
                }

                $select.select2({
                    placeholder: "Buscar",
                    width: "100%",
                    ajax: {
                        transport: function (params, success, failure) {
            const payload = {
                model: model,
                term: params.data.term || "",
                depend: depend ? depSelect.value : null
            };

            fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(r => r.json())
            .then(success)
            .catch(failure);
        },
        processResults: data => ({ results: data.results })
                        /*url,
                        dataType: "json",
                        delay: 250,
                        data: params => {
                            if (depend && (!depSelect || !depSelect.value)) return null;
                            return {
                                model,
                                term: params.term || "",
                                ...(depend && depSelect.value && { [`depend_${depend}`]: depSelect.value })
                            };
                        },
                        processResults: data => ({ results: data.results }),
                        cache: true*/
                    },
                    minimumInputLength: 3,
                    dropdownParent:  $(select).closest('.modal-content').length ? $(select).closest('.modal-content') : null
                });
            }

            if (depend && depSelect) {
                $(depSelect).on("change", () => {
                    if (type === "source") {
                        $select.val(null).trigger("change");
                    } else {
                        loadStatic();
                    }
                });
            }
        });
    }

    function on(eventName, fn) {
        if (events[eventName]) events[eventName].push(fn);
    }
    return { init, on };
})();
document.addEventListener("DOMContentLoaded", () => VladikSelect.init());
document.addEventListener('htmx:afterSwap', (e) => {
    if (e.target && e.target.closest('.modal-content')) {
        VladikSelect.init(e.target);
    }
});

document.addEventListener('shown.bs.modal', e => VladikSelect.init(e.target));

document.addEventListener('hidden.bs.modal', function(e) {
    e.target.querySelectorAll('select[data-select]').forEach(sel => {
        const $sel = $(sel);
        if ($sel.data('select2')) $sel.select2('destroy');
        sel.removeAttribute("data-vladik-select-init");
    });
});
