import re
from datetime import datetime
from django.core.exceptions import ValidationError

def validate_cpf(cpf):
    """
    Validates a Brazilian CPF (Cadastro de Pessoas Físicas).
    """
    if not cpf:
        return False
        
    cpf = "".join(filter(str.isdigit, str(cpf)))
    
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
        
    def calculate_digit(cpf, weights):
        sum_val = sum(int(digit) * weight for digit, weight in zip(cpf, weights))
        remainder = sum_val % 11
        return 0 if remainder < 2 else 11 - remainder
        
    weights1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    weights2 = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    
    if int(cpf[9]) != calculate_digit(cpf[:9], weights1):
        return False
    if int(cpf[10]) != calculate_digit(cpf[:10], weights2):
        return False
        
    return True

def validate_cnpj(cnpj):
    """
    Validates a Brazilian CNPJ (Cadastro Nacional da Pessoa Jurídica).
    """
    if not cnpj:
        return False
        
    cnpj = "".join(filter(str.isdigit, str(cnpj)))
    
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
        
    def calculate_digit(cnpj, weights):
        sum_val = sum(int(digit) * weight for digit, weight in zip(cnpj, weights))
        remainder = sum_val % 11
        return 0 if remainder < 2 else 11 - remainder
        
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    if int(cnpj[12]) != calculate_digit(cnpj[:12], weights1):
        return False
    if int(cnpj[13]) != calculate_digit(cnpj[:13], weights2):
        return False
        
    return True

def validate_email(email):
    """
    Validates a basic email format using regular expressions.
    """
    if not email:
        return True
        
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, str(email)))

def validate_phone(phone):
    """
    Validates a Brazilian phone number.
    """
    if not phone:
        return False
        
    phone = "".join(filter(str.isdigit, str(phone)))
    return len(phone) in (10, 11)

def validate_zip_code(zip_code):
    """
    Validates a Brazilian ZIP code (CEP).
    """
    if not zip_code:
        return False
        
    zip_code = "".join(filter(str.isdigit, str(zip_code)))
    return len(zip_code) == 8

def validate_date(date_str, fmt='%d/%m/%Y'):
    """
    Validates if a string or date object is a valid date.
    """
    if not date_str:
        return False
        
    if hasattr(date_str, 'year') and hasattr(date_str, 'month') and hasattr(date_str, 'day'):
        return True
        
    try:
        datetime.strptime(str(date_str), fmt)
        return True
    except (ValueError, TypeError):
        return False

def validate_url(url):
    """
    Validates if a string is a properly formatted URL.
    """
    if not url:
        return True
        
    url_regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(re.match(url_regex, str(url)))

def validate_iban(iban):
    """
    Validates a basic IBAN format.
    """
    if not iban:
        return False
    iban_regex = r'^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$'
    return bool(re.match(iban_regex, str(iban).replace(' ', '').upper()))

def validate_upload_files_docs(value):
    """
    Validates that an uploaded file has a permitted extension.
    """
    if not value or not hasattr(value, 'name'):
        return
    ext = value.name.split('.')[-1].lower()
    if ext not in ['txt', 'doc', 'docx', 'odt', 'rtf', 'pdf']:
        raise ValidationError('Apenas arquivos .txt, .doc, .docx, .odt, .rtf e .pdf são permitidos.')
