class CondominiumDTO:
    def __init__(self, id, code, name, cnpj, is_active, state_registration, municipal_registration, type_condominium_id, struction_condominium_id, address_id):
        self.id = id
        self.code = code
        self.name = name
        self.cnpj = cnpj
        self.is_active = is_active
        self.state_registration = state_registration
        self.municipal_registration = municipal_registration
        self.type_condominium_id = type_condominium_id
        self.struction_condominium_id = struction_condominium_id
        self.address_id = address_id

    @classmethod
    def from_model(cls, condominium):
        return cls(
            id=condominium.id,
            code=condominium.code,
            name=condominium.name,
            cnpj=condominium.cnpj,
            is_active=condominium.is_active,
            state_registration=condominium.state_registration,
            municipal_registration=condominium.municipal_registration,
            type_condominium_id=condominium.type_condominium.id,
            struction_condominium_id=condominium.struction_condominium.id if condominium.struction_condominium else None,
            address_id=condominium.address.id
        )
