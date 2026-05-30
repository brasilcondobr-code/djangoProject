from domains.residents.models import RealEstateAgency

class RealEstateAgencyDTO:
    def __init__(self, id, condo_unit_id, name, trade_name, cnpj, phone, email, website, address_id, contact_person, is_active, created_at, updated_at):
        self.id = id
        self.condo_unit_id = condo_unit_id
        self.name = name
        self.trade_name = trade_name
        self.cnpj = cnpj
        self.phone = phone
        self.email = email
        self.website = website
        self.address_id = address_id
        self.contact_person = contact_person
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_model(cls, agency):
        return cls(
            id=agency.id,
            condo_unit_id=agency.condo_unit.id if agency.condo_unit else None,
            name=agency.name,
            trade_name=agency.trade_name,
            cnpj=agency.cnpj,
            phone=agency.phone,
            email=agency.email,
            website=agency.website,
            address_id=agency.address.id if agency.address else None,
            contact_person=agency.contact_person,
            is_active=agency.is_active,
            created_at=agency.created_at,
            updated_at=agency.updated_at
        )
