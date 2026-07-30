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


def validate_agency(value):
    if not value:
        raise ValidationError('A agência é obrigatória.')
    import re
    pattern = r'^\d{1,6}$'
    if not re.match(pattern, value):
        raise ValidationError('A agência deve conter apenas números (até 6 dígitos).')


def validate_account_number(value):
    if not value:
        raise ValidationError('O número da conta é obrigatório.')
    import re
    pattern = r'^\d{1,10}$'
    if not re.match(pattern, value):
        raise ValidationError('O número da conta deve conter apenas números (até 10 dígitos).')


def validate_initial_balance(value):
    if value is None:
        return
    if value < 0:
        raise ValidationError('O saldo inicial não pode ser negativo.')


def validate_chart_account_code(value):
    if not value:
        raise ValidationError('O código da conta é obrigatório.')
    value = value.strip()
    if not re.match(r'^[\d.]+$', value):
        raise ValidationError('O código da conta deve conter apenas números e pontos.')
    segments = value.split('.')
    if len(segments) > 4:
        raise ValidationError('O código da conta possui muitos segmentos.')
    for segment in segments:
        if not segment or len(segment) > 3:
            raise ValidationError('Cada segmento do código deve ter de 1 a 3 dígitos.')


def validate_external_reference(value):
    if not value:
        return
    if not re.match(r'^[A-Za-z0-9\-]+$', value):
        raise ValidationError('A referência externa deve conter apenas letras, números e hífen.')
    if len(value) > 50:
        raise ValidationError('A referência externa deve ter no máximo 50 caracteres.')


def validate_archive_reason(value):
    if not value:
        return
    if not value.strip():
        raise ValidationError('O motivo do arquivamento não pode conter apenas espaços.')
    if len(value) > 255:
        raise ValidationError('O motivo do arquivamento deve ter no máximo 255 caracteres.')


def validate_task_title(value):
    if not value:
        raise ValidationError('Informe o título da tarefa.')
    stripped = value.strip()
    if not stripped:
        raise ValidationError('O título da tarefa não pode conter apenas espaços.')
    if len(stripped) > 255:
        raise ValidationError('O título da tarefa deve ter no máximo 255 caracteres.')
    return stripped


def validate_task_description(value):
    if is_html_content_empty(value):
        raise ValidationError('A descrição da tarefa deve possuir conteúdo.')
    _reject_dangerous_html(value)


def validate_task_history_description(value):
    if is_html_content_empty(value):
        raise ValidationError('A descrição do histórico deve possuir conteúdo.')
    _reject_dangerous_html(value)


def _reject_dangerous_html(value):
    import re
    for tag in ['script', 'iframe', 'object', 'embed']:
        pattern = rf'<{tag}[^>]*>.*?</{tag}>'
        matches = re.findall(pattern, value, re.IGNORECASE | re.DOTALL)
        if matches:
            raise ValidationError(f'A descrição contém tags {tag} não permitidas.')
    dangerous_attrs = re.findall(r'\son\w+\s*=', value, re.IGNORECASE)
    if dangerous_attrs:
        raise ValidationError('A descrição contém atributos de evento não permitidos.')

