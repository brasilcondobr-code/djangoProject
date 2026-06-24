from django import forms
from django.urls import reverse_lazy

from core.services.validators import validate_date
from domains.administrative.models.circular import Circular
from domains.residents.models import Resident
from domains.parameters.models import ResidentType
from ckeditor.widgets import CKEditorWidget


class CircularForm(forms.ModelForm):
    class Meta:
        model = Circular
        fields = "__all__"

        widgets = {
            "circular_content": CKEditorWidget(),
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
                }
            ),
            "types_residents": forms.Select(
                attrs={
                    "class": "form-control",
                    "data-residents-url": reverse_lazy("get_residents_by_type"),
                }
            ),
            "residents": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                    "data-placeholder": "Selecione os moradores",
                }
            ),
        }

        labels = {
            "condominium": "Condomínio",
            "release_date": "Data de Lançamento",
            "title": "Título",
            "circular_content": "Conteúdo da Circular",
            "is_active": "Ativo",
            "connection_status": "Status",
            "types_residents": "Tipo de Residente",
            "residents": "Residentes",
            "email_smtp_configuration": "Configuração SMTP",
        }

        help_texts = {
            "types_residents": "Selecione o tipo de residente para filtrar os moradores.",
            "residents": "Após selecionar o tipo de residente, escolha um ou vários moradores.",
        }

        error_messages = {
            "condominium": {
                "required": "O condomínio é obrigatório.",
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

        self.fields["condominium"].required = True
        self.fields["release_date"].required = True
        self.fields["title"].required = True
        self.fields["circular_content"].required = True

        self.fields["residents"].queryset = Resident.objects.none()

        resident_type_id = self._resolve_resident_type_id()

        if resident_type_id:
            try:
                resident_type_id = int(resident_type_id)

                if not self.is_bound:
                    self.fields["types_residents"].initial = resident_type_id

                self.fields["residents"].queryset = Resident.objects.filter(
                    type_of_resident_id=resident_type_id
                ).order_by("name")

            except (TypeError, ValueError):
                self.fields["residents"].queryset = Resident.objects.none()

    def _resolve_resident_type_id(self):
        """
        Resolve o tipo de residente considerando:
        1. POST/GET do formulário;
        2. instância existente;
        3. valor inicial;
        4. tipo padrão Morador(a) na tela de adicionar.
        """

        if self.data.get("types_residents"):
            return self.data.get("types_residents")

        if self.instance and self.instance.pk and self.instance.types_residents_id:
            return self.instance.types_residents_id

        initial_type = self.initial.get("types_residents")
        if initial_type:
            return initial_type

        if not self.is_bound and not self.instance.pk:
            default_type_id = ResidentType.objects.filter(
                description__iexact="Morador(a)"
            ).values_list("id", flat=True).first()

            return default_type_id

        return None

    def clean(self):
        cleaned_data = super().clean()
        types_residents = cleaned_data.get("types_residents")
        residents = cleaned_data.get("residents")

        if types_residents and residents:
            selected_resident_ids = set(residents.values_list("id", flat=True))

            compatible_resident_ids = set(
                residents.filter(
                    type_of_resident_id=types_residents.id
                ).values_list("id", flat=True)
            )

            if not selected_resident_ids.issubset(compatible_resident_ids):
                raise forms.ValidationError(
                    "Existem residentes selecionados incompatíveis com o tipo de residente informado."
                )

        return cleaned_data

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
