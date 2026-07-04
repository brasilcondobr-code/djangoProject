from pathlib import Path
import re
from html import unescape

from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

ALLOWED_INFRACTION_FILE_EXTENSIONS = {
    ".doc",
    ".docx",
    ".pdf",
    ".odt",
    ".txt",
    ".rtf",
}

def validate_infraction_file_extension(file):
    if not file:
        return

    extension = Path(file.name).suffix.lower()

    if extension not in ALLOWED_INFRACTION_FILE_EXTENSIONS:
        raise ValidationError(
            "Formato de arquivo inválido. "
            "São permitidos apenas arquivos .doc, .docx, .pdf, "
            ".odt, .txt e .rtf."
        )

def is_html_content_empty(value):
    if not value:
        return True

    text = strip_tags(value)
    text = unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", "", text)

    return not bool(text)
