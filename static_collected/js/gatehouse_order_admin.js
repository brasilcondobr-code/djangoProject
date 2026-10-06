document.addEventListener("DOMContentLoaded", function () {
    var input = document.getElementById("id_photos");
    if (!input) {
        return;
    }

    var STANDARD_IMAGE = /\.(jpe?g|png)$/i;
    // Guarda o que já foi escolhido: cada clique no botão "Foto" abre o
    // seletor/câmera e a nova seleção substituiria as anteriores.
    var kept = [];

    input.addEventListener("click", function () {
        kept = Array.prototype.slice.call(input.files || []);
    });

    // Converte capturas em arquivos de imagem padrão (.jpg): a câmera pode
    // entregar HEIC/WEBP/etc e o servidor aceita apenas .jpg/.jpeg/.png.
    function toStandardImage(file) {
        if (STANDARD_IMAGE.test(file.name)) {
            return Promise.resolve(file);
        }
        return new Promise(function (resolve) {
            var url = URL.createObjectURL(file);
            var img = new Image();
            img.onload = function () {
                var canvas = document.createElement("canvas");
                canvas.width = img.naturalWidth || 1;
                canvas.height = img.naturalHeight || 1;
                canvas.getContext("2d").drawImage(img, 0, 0);
                URL.revokeObjectURL(url);
                if (typeof canvas.toBlob !== "function") {
                    resolve(file);
                    return;
                }
                canvas.toBlob(
                    function (blob) {
                        if (!blob) {
                            resolve(file);
                            return;
                        }
                        var base = file.name.replace(/\.[^.]+$/, "") || "foto";
                        resolve(
                            new File([blob], base + ".jpg", {
                                type: "image/jpeg",
                                lastModified: Date.now(),
                            })
                        );
                    },
                    "image/jpeg",
                    0.9
                );
            };
            img.onerror = function () {
                // Navegador não decodifica o formato (ex.: HEIC fora da Apple);
                // mantém o original e o servidor valida/recusa normalmente.
                URL.revokeObjectURL(url);
                resolve(file);
            };
            img.src = url;
        });
    }

    input.addEventListener("change", function () {
        var fresh = Array.prototype.slice.call(input.files || []);
        Promise.all(fresh.map(toStandardImage)).then(function (converted) {
            var merged = kept.concat(converted);
            var dt = new DataTransfer();
            merged.forEach(function (file) {
                dt.items.add(file);
            });
            input.files = dt.files;
            kept = merged;
        });
    });
});
