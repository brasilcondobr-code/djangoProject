from django import forms

from core.services.validators import validate_date
from domains.administrative.models.documents import Documents
from domains.administrative.services.document_validator_service import validate_document_file_extension
from domains.administrative.services.document_service import DocumentService

class DocumentsForm(forms.ModelForm):
    class Meta:
        model = Documents
        fields = "__all__"

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Informe o título do documento",
                }
            ),
            "registration_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "observations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Informe observações sobre o documento",
                }
            ),
        }

        labels = {
            "condominium": "Condomínio",
            "document_type": "Tipo de Documento",
            "title": "Título do Documento",
            "registration_date": "Data de Registro",
            "file": "Arquivo do Documento",
            "observations": "Observações",
            "is_active": "Ativo",
        }

        help_texts = {
            "file": "Formatos permitidos: .doc, .docx, .pdf, .odt, .txt e .rtf.",
            "registration_date": "Informe a data de registro do documento.",
        }

        error_messages = {
            "condominium": {
                "required": "O condomínio é obrigatório.",
            },
            "document_type": {
                "required": "O tipo de documento é obrigatório.",
            },
            "title": {
                "required": "O título do documento é obrigatório.",
            },
            "registration_date": {
                "required": "A data de registro é obrigatória.",
                "invalid": "Informe uma data válida.",
            },
            "file": {
                "required": "O arquivo do documento é obrigatório.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["condominium"].required = True
        self.fields["document_type"].required = True
        self.fields["title"].required = True
        self.fields["registration_date"].required = True
        self.fields["file"].required = True

        # Garante que a data seja exibida no formato YYYY-MM-DD para o input type="date" do HTML5
        if self.instance and self.instance.pk and self.instance.registration_date:
            if not self.is_bound:
                self.initial['registration_date'] = self.instance.registration_date.strftime('%Y-%m-%d')


    def clean_title(self):
        title = self.cleaned_data.get("title")
        if not title or not title.strip():
            raise forms.ValidationError("O título do documento é obrigatório.")
        return title.strip()

    def clean_registration_date(self):
        registration_date = self.cleaned_data.get("registration_date")
        if not registration_date:
            raise forms.ValidationError("A data de registro é obrigatória.")
        if not validate_date(registration_date):
            raise forms.ValidationError("A data de registro informada é inválida.")
        return registration_date

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if not file:
            raise forms.ValidationError("O arquivo do documento é obrigatório.")
        validate_document_file_extension(file)
        return file

    def clean(self):
        cleaned_data = super().clean()

        condominium = cleaned_data.get("condominium")
        title = cleaned_data.get("title")
        registration_date = cleaned_data.get("registration_date")

        if condominium and title and registration_date:
            exists = DocumentService.document_exists_for_condominium(
                condominium=condominium,
                title=title,
                registration_date=registration_date,
                exclude_id=self.instance.pk if self.instance else None,
            )

            if exists:
                raise forms.ValidationError(
                    "Já existe um documento com este título e data de registro para o condomínio selecionado."
                )

        return cleaned_data
