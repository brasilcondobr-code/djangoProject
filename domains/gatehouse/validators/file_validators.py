"""Validação de arquivos do módulo 04. Encomendas (gatehouse)."""

from pathlib import Path

from django.core.exceptions import ValidationError

ALLOWED_ORDER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_ORDER_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

_EXTENSION_ORDER = (".jpg", ".jpeg", ".png", ".pdf")

_SIGNATURES = {
    ".pdf": (b"%PDF-",),
    ".jpg": (b"\xFF\xD8\xFF",),
    ".jpeg": (b"\xFF\xD8\xFF",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
}


def validate_order_file(file, extensions=None):
    """Valida extensão, tamanho e assinatura de conteúdo do arquivo.

    A assinatura é lida do próprio conteúdo (não se confia na extensão nem
    no Content-Type enviados pelo cliente). O ponteiro do arquivo é
    reposicionado no início ao final da validação.

    ``extensions`` restringe os formatos aceitos (padrão: todos do módulo;
    as fotos usam ``IMAGE_EXTENSIONS``).
    """
    if not file or not hasattr(file, "name"):
        raise ValidationError("O arquivo é obrigatório.")

    allowed = ALLOWED_ORDER_EXTENSIONS if extensions is None else set(extensions)
    extension = Path(file.name).suffix.lower()
    if extension not in allowed:
        ordered = [e for e in _EXTENSION_ORDER if e in allowed]
        listed = ", ".join(ordered[:-1]) + " ou " + ordered[-1]
        raise ValidationError(
            "Formato de arquivo inválido. Utilize apenas %s." % listed
        )

    if file.size == 0:
        raise ValidationError("O arquivo está vazio.")

    if file.size > MAX_ORDER_FILE_SIZE:
        raise ValidationError("O arquivo não pode ultrapassar 10 MB.")

    try:
        header = file.read(8)
    finally:
        file.seek(0)

    if not header.startswith(_SIGNATURES[extension]):
        raise ValidationError(
            "O conteúdo do arquivo não corresponde ao formato informado."
        )
