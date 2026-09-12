from shared.validators import validate_cnpj

class CondominiumValidator:
    @staticmethod
    def validate_cnpj(cnpj):
        if not validate_cnpj(cnpj):
            raise ValueError("CNPJ inválido.")
