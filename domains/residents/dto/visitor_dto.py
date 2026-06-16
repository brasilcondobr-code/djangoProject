from domains.residents.models import Visitor

class VisitorDTO:
    def __init__(self, id, condo_unit_id, name, cpf, rg, phone, purpose, photo, is_active, situation, regular, death, api_status, retorno_api, date_time_appointment, certificate_presentation_date, certificate_validity, observations_certificate, certificate_file, types_visitor_restriction_id, restrictionVisitor_presentation_date, restrictionVisitor_validity_date, restrictionVisitor_observations, restrictionVisitor_file, created_at, updated_at):
        self.id = id
        self.condo_unit_id = condo_unit_id
        self.name = name
        self.cpf = cpf
        self.rg = rg
        self.phone = phone
        self.purpose = purpose
        self.photo = photo
        self.is_active = is_active
        self.situation = situation
        self.regular = regular
        self.death = death
        self.api_status = api_status
        self.retorno_api = retorno_api
        self.date_time_appointment = date_time_appointment
        self.certificate_presentation_date = certificate_presentation_date
        self.certificate_validity = certificate_validity
        self.observations_certificate = observations_certificate
        self.certificate_file = certificate_file
        self.types_visitor_restriction_id = types_visitor_restriction_id
        self.restrictionVisitor_presentation_date = restrictionVisitor_presentation_date
        self.restrictionVisitor_validity_date = restrictionVisitor_validity_date
        self.restrictionVisitor_observations = restrictionVisitor_observations
        self.restrictionVisitor_file = restrictionVisitor_file
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_model(cls, visitor):
        return cls(
            id=visitor.id,
            condo_unit_id=visitor.condo_unit.id if visitor.condo_unit else None,
            name=visitor.name,
            cpf=visitor.cpf,
            rg=visitor.rg,
            phone=visitor.phone,
            purpose=visitor.purpose,
            photo=visitor.photo.name if visitor.photo else None,
            is_active=visitor.is_active,
            situation=visitor.situation,
            regular=visitor.regular,
            death=visitor.death,
            api_status=visitor.api_status,
            retorno_api=visitor.retorno_api,
            date_time_appointment=visitor.date_time_appointment,
            certificate_presentation_date=visitor.certificate_presentation_date,
            certificate_validity=visitor.certificate_validity,
            observations_certificate=visitor.observations_certificate,
            certificate_file=visitor.certificate_file.name if visitor.certificate_file else None,
            types_visitor_restriction_id=visitor.types_visitor_restriction.id if visitor.types_visitor_restriction else None,
            restrictionVisitor_presentation_date=visitor.restrictionVisitor_presentation_date,
            restrictionVisitor_validity_date=visitor.restrictionVisitor_validity_date,
            restrictionVisitor_observations=visitor.restrictionVisitor_observations,
            restrictionVisitor_file=visitor.restrictionVisitor_file.name if visitor.restrictionVisitor_file else None,
            created_at=visitor.created_at,
            updated_at=visitor.updated_at
        )
