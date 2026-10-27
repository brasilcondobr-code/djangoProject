document.addEventListener("DOMContentLoaded", function () {
    var input = document.getElementById("id_photos");
    if (!input) {
        return;
    }

    var STANDARD_IMAGE = /\.(jpe?g|png)$/i;
    // Guarda o que já foi escolhido (câmera e seletor de arquivos): a cada
    // seleção nova o navegador substitui a anterior, então sincronizamos
    // sempre por aqui.
    var kept = [];
    var seq = 0;

    input.addEventListener("click", function () {
        kept = Array.prototype.slice.call(input.files || []);
    });

    function sync(files) {
        kept = files;
        var dt = new DataTransfer();
        kept.forEach(function (file) {
            dt.items.add(file);
        });
        input.files = dt.files;
    }

    // Converte capturas do seletor em imagem padrão (.jpg): a câmera pode
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
                // Navegador não decodifica o formato; mantém o original e o
                // servidor valida/recusa normalmente.
                URL.revokeObjectURL(url);
                resolve(file);
            };
            img.src = url;
        });
    }

    input.addEventListener("change", function () {
        var fresh = Array.prototype.slice.call(input.files || []);
        Promise.all(fresh.map(toStandardImage)).then(function (converted) {
            sync(kept.concat(converted));
        });
    });

    /* ---------------- câmera do navegador (getUserMedia) ---------------- */

    var label = document.querySelector('label[for="id_photos"]');
    if (!label) {
        return;
    }

    label.addEventListener("click", function (event) {
        // O botão "Foto" não abre o seletor de arquivos: abre a câmera.
        event.preventDefault();
        openCamera().catch(function (error) {
            var name = (error && error.name) || "";
            if (name === "NotAllowedError" || name === "NotFoundError" ||
                    name === "NotReadableError" || name === "OverconstrainedError") {
                window.alert(
                    "Não foi possível usar a câmera (" + name + ").\n" +
                    "Verifique a permissão do navegador. Alternando para o " +
                    "selecionador de arquivos."
                );
            }
            // Fallback: seletor de arquivos do próprio input (capture=...).
            input.click();
        });
    });

    function openCamera() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            return Promise.reject({ name: "UnsupportedError" });
        }
        if (document.getElementById("bc-order-camera")) {
            return Promise.resolve();
        }
        return navigator.mediaDevices
            .getUserMedia({
                video: { facingMode: { ideal: "environment" } },
                audio: false,
            })
            .then(function (stream) {
                mountCamera(stream);
            });
    }

    function mountCamera(stream) {
        var overlay = document.createElement("div");
        overlay.id = "bc-order-camera";
        overlay.style.cssText =
            "position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.88);" +
            "display:flex;flex-direction:column;align-items:center;" +
            "justify-content:center;font-family:sans-serif;";

        var video = document.createElement("video");
        video.autoplay = true;
        video.playsInline = true;
        video.muted = true;
        video.style.cssText =
            "max-width:92vw;max-height:62vh;background:#000;border-radius:8px;";
        video.srcObject = stream;

        var counter = document.createElement("p");
        counter.style.cssText = "color:#fff;margin:10px 0 6px;font-size:14px;";
        var taken = 0;
        counter.textContent = "0 foto(s) nesta sessão";

        var bar = document.createElement("div");
        bar.style.cssText = "display:flex;gap:8px;";

        var shoot = document.createElement("button");
        shoot.type = "button";
        shoot.className = "btn btn-success";
        shoot.textContent = "Tirar foto";

        var close = document.createElement("button");
        close.type = "button";
        close.className = "btn btn-secondary";
        close.textContent = "Concluir";

        function stopCamera() {
            stream.getTracks().forEach(function (track) {
                track.stop();
            });
            if (overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }
        }

        shoot.addEventListener("click", function () {
            var width = video.videoWidth;
            var height = video.videoHeight;
            if (!width || !height) {
                return;
            }
            var canvas = document.createElement("canvas");
            if (typeof canvas.toBlob !== "function") {
                return;
            }
            canvas.width = width;
            canvas.height = height;
            canvas.getContext("2d").drawImage(video, 0, 0);
            canvas.toBlob(
                function (blob) {
                    if (!blob) {
                        return;
                    }
                    seq += 1;
                    var file = new File(
                        [blob],
                        "foto-" + Date.now() + "-" + seq + ".jpg",
                        { type: "image/jpeg", lastModified: Date.now() }
                    );
                    sync(kept.concat([file]));
                    taken += 1;
                    counter.textContent = taken + " foto(s) nesta sessão";
                },
                "image/jpeg",
                0.9
            );
        });

        close.addEventListener("click", stopCamera);

        bar.appendChild(shoot);
        bar.appendChild(close);
        overlay.appendChild(video);
        overlay.appendChild(counter);
        overlay.appendChild(bar);
        document.body.appendChild(overlay);
        video.play().catch(function () {});
    }
});
