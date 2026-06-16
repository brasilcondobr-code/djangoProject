class PersonalitiesValidator:
    @staticmethod
    def validate_entity(data):
        if 'code' not in data or not data['code']:
            raise ValueError("Código é obrigatório.")
        if 'cpf_cnpj' not in data or not data['cpf_cnpj']:
            raise ValueError("CPF/CNPJ é obrigatório.")
        if 'name' not in data or not data['name']:
            raise ValueError("Nome é obrigatório.")
        if 'email' not in data or not data['email']:
            raise ValueError("E-mail é obrigatório.")
        if 'phone' not in data or not data['phone']:
            raise ValueError("Telefone é obrigatório.")

    @staticmethod
    def validate_business_sector(data):
        if 'description' not in data or not data['description']:
            raise ValueError("Descrição é obrigatória.")
