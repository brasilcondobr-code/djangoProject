class ResidentDTO:
    def __init__(self, id, unit_id, type_of_resident_id, name, email, phone, cpf, rg, sex, date_of_birth, profission, is_primary, is_resident, is_active, photo, situation, regular, death, api_status, retorno_api, date_time_appointment, certificate_presentation_date, certificate_validity, observations_certificate, certificate_file, created_at, updated_at):
        self.id = id
        self.unit_id = unit_id
        self.type_of_resident_id = type_of_resident_id
        self.name = name
        self.email = email
        self.phone = phone
        self.cpf = cpf
        self.rg = rg
        self.sex = sex
        self.date_of_birth = date_of_birth
        self.profission = profission
        self.is_primary = is_primary
        self.is_resident = is_resident
        self.is_active = is_active
        self.photo = photo
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
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_model(cls, resident):
        return cls(
            id=resident.id,
            unit_id=resident.unit.id,
            type_of_resident_id=resident.type_of_resident.id if resident.type_of_resident else None,
            name=resident.name,
            email=resident.email,
            phone=resident.phone,
            cpf=resident.cpf,
            rg=resident.rg,
            sex=resident.sex,
            date_of_birth=resident.date_of_birth,
            profission=resident.profission,
            is_primary=resident.is_primary,
            is_resident=resident.is_resident,
            is_active=resident.is_active,
            photo=resident.photo.name if resident.photo else None,
            situation=resident.situation,
            regular=resident.regular,
            death=resident.death,
            api_status=resident.api_status,
            retorno_api=resident.retorno_api,
            date_time_appointment=resident.date_time_appointment,
            certificate_presentation_date=resident.certificate_presentation_date,
            certificate_validity=resident.certificate_validity,
            observations_certificate=resident.observations_certificate,
            certificate_file=resident.certificate_file.name if resident.certificate_file else None,
            created_at=resident.created_at,
            updated_at=resident.updated_at
        )
