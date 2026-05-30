from domains.personalities.models.entity import Entity

class EntityDTO:
    def __init__(self, id=None, code=None, kind=None, business_sector_id=None, name=None, trade_name=None, cpf_cnpj=None, rg_ie=None, municipal_registration=None, date_of_birth_opening=None, sex=None, email=None, phone=None, address_id=None, observations=None, is_active=True, situation=None, regular=None, death=None, api_status=None, retorno_api=None, date_time_appointment=None, created_at=None, updated_at=None):
        self.id = id
        self.code = code
        self.kind = kind
        self.business_sector_id = business_sector_id
        self.name = name
        self.trade_name = trade_name
        self.cpf_cnpj = cpf_cnpj
        self.rg_ie = rg_ie
        self.municipal_registration = municipal_registration
        self.date_of_birth_opening = date_of_birth_opening
        self.sex = sex
        self.email = email
        self.phone = phone
        self.address_id = address_id
        self.observations = observations
        self.is_active = is_active
        self.situation = situation
        self.regular = regular
        self.death = death
        self.api_status = api_status
        self.retorno_api = retorno_api
        self.date_time_appointment = date_time_appointment
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_model(cls, entity):
        return cls(
            id=entity.id,
            code=entity.code,
            kind=entity.kind,
            business_sector_id=entity.business_sector.id if entity.business_sector else None,
            name=entity.name,
            trade_name=entity.trade_name,
            cpf_cnpj=entity.cpf_cnpj,
            rg_ie=entity.rg_ie,
            municipal_registration=entity.municipal_registration,
            date_of_birth_opening=entity.date_of_birth_opening,
            sex=entity.sex,
            email=entity.email,
            phone=entity.phone,
            address_id=entity.address.id if entity.address else None,
            observations=entity.observations,
            is_active=entity.is_active,
            situation=entity.situation,
            regular=entity.regular,
            death=entity.death,
            api_status=entity.api_status,
            retorno_api=entity.retorno_api,
            date_time_appointment=entity.date_time_appointment,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
