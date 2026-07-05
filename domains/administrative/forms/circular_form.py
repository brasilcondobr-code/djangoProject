from django import forms
from django.urls import reverse_lazy

from core.services.validators import validate_date
from domains.administrative.models.circular import Circular
from domains.email_service.models import ConnectionStatus
from ckeditor.widgets import CKEditorWidget


class CircularForm(forms.ModelForm):
    class Meta:
        model = Circular
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
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Informe o título da circular",
                }
            ),
            "release_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "circular_content": CKEditorWidget(),
        }

        labels = {
            "condominium": "Condomínio",
            "types_residents": "Tipos de Residentes",
            "release_date": "Data de Lançamento",
            "title": "Título",
            "circular_content": "Conteúdo da Circular",
            "is_active": "Ativo",
            "connection_status": "Status",
            "email_smtp_configuration": "Configuração SMTP",
        }

        error_messages = {
            "condominium": {
                "required": "O condomínio é obrigatório.",
            },
            "types_residents": {
                "required": "A seleção de tipos de residentes é obrigatória.",
            },
            "release_date": {
                "required": "A data de lançamento é obrigatória.",
                "invalid": "Informe uma data válida.",
            },
            "title": {
                "required": "O título é obrigatório.",
            },
            "circular_content": {
                "required": "O conteúdo da circular é obrigatório.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = [
            "condominium",
            "types_residents",
            "release_date",
            "title",
            "circular_content",
        ]

        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

        # Default status to 'Pendente' on creation
        if not self.instance.pk and "connection_status" in self.fields:
            status_pendente = ConnectionStatus.objects.filter(status__iexact='Pendente').first()
            if status_pendente:
                self.fields["connection_status"].initial = status_pendente

    def clean_release_date(self):
        release_date = self.cleaned_data.get("release_date")

        if release_date and not validate_date(release_date):
            raise forms.ValidationError(
                "A data de lançamento informada é inválida."
            )

        return release_date

    def clean_title(self):
        title = self.cleaned_data.get("title")

        if not title or not title.strip():
            raise forms.ValidationError(
                "O título da circular é obrigatório."
            )

        return title.strip()

    def clean_circular_content(self):
        circular_content = self.cleaned_data.get("circular_content")

        if not circular_content or not circular_content.strip():
            raise forms.ValidationError(
                "O conteúdo da circular é obrigatório."
            )

        return circular_content
