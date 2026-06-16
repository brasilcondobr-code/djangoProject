from shared.validators import validate_cpf, validate_email, validate_phone

class ResidentValidator:
    @staticmethod
    def validate_cpf(cpf):
        if not validate_cpf(cpf):
            raise ValueError("CPF inválido.")

    @staticmethod
    def validate_email(email):
        if not validate_email(email):
            raise ValueError("E-mail inválido.")

    @staticmethod
    def validate_phone(phone):
        if not validate_phone(phone):
            raise ValueError("Telefone inválido.")
