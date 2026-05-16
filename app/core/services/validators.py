import re
from datetime import datetime

# ==============================================================================
# CORE VALIDATORS SERVICE
# ==============================================================================
# This module centralizes all validation logic for the project, ensuring
# consistency across different modules and adhering to Clean Architecture.
# ==============================================================================

def validate_cpf(cpf):
    """
    Validates a Brazilian CPF (Cadastro de Pessoas Físicas).
    
    Args:
        cpf (str): The CPF string to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    if not cpf:
        return False
        
    # Remove non-numeric characters
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
    
    Args:
        cnpj (str): The CNPJ string to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    if not cnpj:
        return False
        
    # Remove non-numeric characters
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
    
    Args:
        email (str): The email string to validate.
        
    Returns:
        bool: True if valid or empty, False otherwise.
    """
    if not email:
        return True
        
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, str(email)))

def validate_phone(phone):
    """
    Validates a Brazilian phone number.
    Accepts formats: (XX) 9XXXX-XXXX or (XX) XXXX-XXXX.
    
    Args:
        phone (str): The phone string to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    if not phone:
        return False
        
    # Remove non-numeric characters
    phone = "".join(filter(str.isdigit, str(phone)))
    
    # Brazilian phones have 10 (landline) or 11 (mobile) digits
    return len(phone) in (10, 11)

def validate_zip_code(zip_code):
    """
    Validates a Brazilian ZIP code (CEP).
    Format: XXXXX-XXX or XXXXXXXXX.
    
    Args:
        zip_code (str): The ZIP code string to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    if not zip_code:
        return False
        
    # Remove non-numeric characters
    zip_code = "".join(filter(str.isdigit, str(zip_code)))
    
    return len(zip_code) == 8

def validate_date(date_str, fmt='%d/%m/%Y'):
    """
    Validates if a string or date object is a valid date.
    If it's a date/datetime object, it's considered valid.
    If it's a string, it's validated against the specified format.
    
    Args:
        date_str (str or date): The date value to validate.
        fmt (str): The expected date format. Defaults to '%d/%m/%Y'.
        
    Returns:
        bool: True if valid, False otherwise.
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
    
    Args:
        url (str): The URL string to validate.
        
    Returns:
        bool: True if valid or empty, False otherwise.
    """
    if not url:
        return True
        
    # Basic URL regex that checks for http/https and a domain
    url_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
    return re.match(url_regex, str(url)) is not None

from django.core.exceptions import ValidationError

def validate_upload_files_docs(value):
    """
    Validates that an uploaded file has a permitted extension.
    Permitted: .txt, .doc, .docx, .odt, .rtf, .pdf
    """
    if not value or not hasattr(value, 'name'):
        return
    ext = value.name.split('.')[-1].lower()
    if ext not in ['txt', 'doc', 'docx', 'odt', 'rtf', 'pdf']:
        raise ValidationError('Apenas arquivos .txt, .doc, .docx, .odt, .rtf e .pdf são permitidos.')
