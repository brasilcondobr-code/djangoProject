class CollaboratorDTO:
    def __init__(self, id, condominium_id, name, cpf, rg, email, phone_number,
                 type_collaborator_id, is_active, photo, observations,
                 situation, regular, death,
                 certificate_presentation_date, certificate_validity,
                 observations_certificate, certificate_file):
        self.id = id
        self.condominium_id = condominium_id
        self.name = name
        self.cpf = cpf
        self.rg = rg
        self.email = email
        self.phone_number = phone_number
        self.type_collaborator_id = type_collaborator_id
        self.is_active = is_active
        self.photo = photo
        self.observations = observations
        self.situation = situation
        self.regular = regular
        self.death = death
        self.certificate_presentation_date = certificate_presentation_date
        self.certificate_validity = certificate_validity
        self.observations_certificate = observations_certificate
        self.certificate_file = certificate_file

    @classmethod
    def from_model(cls, collaborator):
        return cls(
            id=collaborator.id,
            condominium_id=collaborator.condominium.id,
            name=collaborator.name,
            cpf=collaborator.cpf,
            rg=collaborator.rg,
            email=collaborator.email,
            phone_number=collaborator.phone_number,
            type_collaborator_id=collaborator.type_collaborator.id if collaborator.type_collaborator else None,
            is_active=collaborator.is_active,
            photo=collaborator.photo,
            observations=collaborator.observations,
            situation=collaborator.situation,
            regular=collaborator.regular,
            death=collaborator.death,
            certificate_presentation_date=collaborator.certificate_presentation_date,
            certificate_validity=collaborator.certificate_validity,
            observations_certificate=collaborator.observations_certificate,
            certificate_file=collaborator.certificate_file,
        )
