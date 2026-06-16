from shared.validators import validate_cpf

class CollaboratorValidator:
    @staticmethod
    def validate_cpf(cpf):
        if not validate_cpf(cpf):
            raise ValueError("CPF inválido.")
