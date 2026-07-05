from domains.administrative.models.documents import Documents

class DocumentService:
    @staticmethod
    def document_exists_for_condominium(condominium, title, registration_date, exclude_id=None):
        """
        Verifica se já existe um documento com o mesmo condomínio, título e data de registro.
        """
        queryset = Documents.objects.filter(
            condominium=condominium,
            title__iexact=title,
            registration_date=registration_date,
        )

        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)

        return queryset.exists()
