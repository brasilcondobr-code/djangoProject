import os
from django.core.exceptions import ValidationError

ALLOWED_DOCUMENT_EXTENSIONS = [
    ".doc",
    ".docx",
    ".pdf",
    ".odt",
    ".txt",
    ".rtf",
]

def validate_document_file_extension(file):
    """
    Valida se a extensão do arquivo enviado é permitida.
    """
    ext = os.path.splitext(file.name)[1].lower()

    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError(
            "Formato de arquivo inválido. São permitidos apenas: .doc, .docx, .pdf, .odt, .txt e .rtf."
        )
