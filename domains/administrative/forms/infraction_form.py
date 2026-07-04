from django import forms
from domains.administrative.models.infraction import Infraction
from domains.administrative.validators import (
    is_html_content_empty,
    validate_infraction_file_extension,
)
from shared.validators import validate_date
from ckeditor.widgets import CKEditorWidget
from domains.email_service.models import ConnectionStatus

class InfractionsForm(forms.ModelForm):
    class Meta:
        model = Infraction
        fields = "__all__"

        widgets = {
            "condominium": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                }
            ),
            "types_residents": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                }
            ),
            "releaseDate": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "placeholder": "Selecione a data de lançamento",
                },
                format="%Y-%m-%d",
            ),
            "infractions_type": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Informe o título da infração",
                    "maxlength": "255",
                }
            ),
            "infractionContent": CKEditorWidget(),
            "file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".doc,.docx,.pdf,.odt,.txt,.rtf",
                }
            ),
        }

        labels = {
            "condominium": "Condomínio",
            "types_residents": "Tipos de Residentes",
            "releaseDate": "Data de Lançamento",
            "infractions_type": "Tipo de Infração",
            "title": "Título",
            "infractionContent": "Conteúdo da Infração",
            "file": "Documento",
            "is_active": "Ativo",
        }

        help_texts = {
            "condominium": "Selecione a unidade condominial vinculada à infração.",
            "releaseDate": "Selecione a data de lançamento da infração.",
            "infractions_type": "Selecione o tipo de infração.",
            "title": "Informe um título único, claro e objetivo.",
            "infractionContent": "Descreva a infração em formato rico/HTML.",
            "file": "Opcional. Formatos aceitos: .doc, .docx, .pdf, .odt, .txt e .rtf.",
        }

        error_messages = {
            "condominium": {
                "required": "O condomínio é obrigatório.",
            },
            "types_residents": {
                "required": "A seleção de tipos de residentes é obrigatória.",
            },
            "releaseDate": {
                "required": "A data de lançamento é obrigatória.",
                "invalid": "Informe uma data válida.",
            },
            "infractions_type": {
                "required": "O tipo de infração é obrigatório.",
            },
            "title": {
                "required": "O título é obrigatório.",
                "unique": "Já existe uma infração cadastrada com este título.",
            },
            "infractionContent": {
                "required": "O conteúdo da infração é obrigatório.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = [
            "condominium",
            "types_residents",
            "releaseDate",
            "infractions_type",
            "title",
            "infractionContent",
        ]

        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

        if "file" in self.fields:
            self.fields["file"].required = False

        # Default status to 'Pendente' on creation
        if not self.instance.pk and "connection_status" in self.fields:
            status_pendente = ConnectionStatus.objects.filter(status__iexact='Pendente').first()
            if status_pendente:
                self.fields["connection_status"].initial = status_pendente

    def clean_title(self):
        title = self.cleaned_data.get("title")

        if not title or not title.strip():
            raise forms.ValidationError("O título é obrigatório.")

        return title.strip()

    def clean_releaseDate(self):
        release_date = self.cleaned_data.get("releaseDate")

        if not release_date:
            raise forms.ValidationError("A data de lançamento é obrigatória.")

        validate_date(release_date)

        return release_date

    def clean_infractionContent(self):
        content = self.cleaned_data.get("infractionContent")

        if is_html_content_empty(content):
            raise forms.ValidationError(
                "O conteúdo da infração é obrigatório."
            )

        return content

    def clean_file(self):
        file = self.cleaned_data.get("file")

        validate_infraction_file_extension(file)

        return file

