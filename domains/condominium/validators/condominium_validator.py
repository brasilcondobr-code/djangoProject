from shared.validators import validate_cnpj, validate_cpf

class CondominiumValidator:
    @staticmethod
    def validate_cnpj(cnpj):
        if not validate_cnpj(cnpj):
            raise ValueError("CNPJ inválido.")

class CollaboratorValidator:
    @staticmethod
    def validate_cpf(cpf):
        if not validate_cpf(cpf):
            raise ValueError("CPF inválido.")
