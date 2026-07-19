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
 
ALLOWED_METER_FILE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
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
 
def validate_meter_file_extension(file):
    if not file:
        raise ValidationError("O arquivo é obrigatório.")
 
    extension = Path(file.name).suffix.lower()
 
    if extension not in ALLOWED_METER_FILE_EXTENSIONS:
        raise ValidationError(
            "Formato de arquivo inválido. "
            "São permitidos apenas arquivos .jpg, .jpeg, .png e .bmp."
        )
 
def validate_meter_composition(value):
    if not value:
        raise ValidationError("A composição é obrigatória.")
 
    pattern = r"^(0[1-9]|1[0-2])\/\d{4}$"
 
    if not re.match(pattern, value):
        raise ValidationError(
            "Informe uma composição válida no formato MM/AAAA."
        )
 
def is_html_content_empty(value):
    if not value:
        return True
 
    text = strip_tags(value)
    text = unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", "", text)
 
    return not bool(text)


def validate_file_size_10mb(file):
    if not file:
        return
    limit = 10 * 1024 * 1024  # 10 MB
    if file.size > limit:
        raise ValidationError("O arquivo não pode ultrapassar 10 MB.")


def validate_photo_extension(file):
    if not file:
        return
    extension = Path(file.name).suffix.lower()
    allowed = {".jpg", ".jpeg", ".png", ".webp"}
    if extension not in allowed:
        raise ValidationError(
            "Formato de imagem inválido. Utilize apenas .jpg, .jpeg, .png ou .webp."
        )


def validate_invoice_extension(file):
    if not file:
        return
    extension = Path(file.name).suffix.lower()
    allowed = {".pdf", ".jpg", ".jpeg", ".png"}
    if extension not in allowed:
        raise ValidationError(
            "Formato de nota fiscal inválido. Utilize apenas .pdf, .jpg, .jpeg ou .png."
        )


def validate_manual_extension(file):
    if not file:
        return
    extension = Path(file.name).suffix.lower()
    allowed = {".pdf", ".doc", ".docx"}
    if extension not in allowed:
        raise ValidationError(
            "Formato de manual inválido. Utilize apenas .pdf, .doc ou .docx."
        )


def validate_warranty_extension(file):
    if not file:
        return
    extension = Path(file.name).suffix.lower()
    allowed = {".pdf", ".jpg", ".jpeg", ".png"}
    if extension not in allowed:
        raise ValidationError(
            "Formato de certificado de garantia inválido. Utilize apenas .pdf, .jpg, .jpeg ou .png."
        )

