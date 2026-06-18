from django import forms
from core.services.validators import validate_date
from domains.administrative.models.circular import Circular
from domains.residents.models import Resident
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

        # Inicia vazio para evitar carregamento de todos os moradores
        self.fields["residents"].queryset = Resident.objects.none()

        resident_type_id = None

        if self.data.get("types_residents"):
            resident_type_id = self.data.get("types_residents")
        elif self.instance and self.instance.pk and self.instance.types_residents_id:
            resident_type_id = self.instance.types_residents_id

        if resident_type_id:
            try:
                resident_type_id = int(resident_type_id)

                self.fields["residents"].queryset = Resident.objects.filter(
                    type_of_resident_id=resident_type_id
                ).order_by("name")

            except (TypeError, ValueError):
                self.fields["residents"].queryset = Resident.objects.none()

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
