from django import forms
from domains.administrative.models.patrimony import Patrimony
from domains.administrative.validators.validators import (
    validate_file_size_10mb,
    validate_photo_extension,
    validate_invoice_extension,
    validate_manual_extension,
    validate_warranty_extension,
)
from core.services.validators import validate_date

class PatrimonyForm(forms.ModelForm):
    purchase_value = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control js-mask-currency",
            "placeholder": "2.500,00",
            "autocomplete": "off",
        }),
        label="Valor de Compra",
    )
    current_value = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control js-mask-currency",
            "placeholder": "2.100,00",
            "autocomplete": "off",
        }),
        label="Valor Atual",
    )
    depreciation_rate = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control js-mask-percentage",
            "placeholder": "35%",
            "autocomplete": "off",
        }),
        label="Taxa de Depreciação",
    )
    useful_life_months = forms.CharField(
        required=False,
        widget=forms.NumberInput(attrs={
            "class": "form-control js-mask-number",
            "placeholder": "60",
            "min": "1",
            "max": "9999",
        }),
        label="Vida Útil em Meses",
    )

    class Meta:
        model = Patrimony
        fields = "__all__"

        widgets = {
            "condominium": forms.Select(
                attrs={"class": "form-control"},
            ),
            "release_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "placeholder": "Selecione a data de lançamento",
                },
                format="%Y-%m-%d",
            ),
            "asset_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "readonly": True,
                    "placeholder": "Gerado automaticamente",
                },
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Computador da administração",
                },
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descrição detalhada do patrimônio...",
                },
            ),
            "asset_type": forms.Select(
                attrs={"class": "form-control"},
            ),
            "asset_category": forms.Select(
                attrs={"class": "form-control"},
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Portaria, Casa de máquinas, Garagem...",
                },
            ),
            "asset_status": forms.Select(
                attrs={"class": "form-control"},
            ),
            "state_condition": forms.Select(
                attrs={"class": "form-control"},
            ),
            "serial_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "SN123456789",
                },
            ),
            "asset_brand": forms.Select(
                attrs={"class": "form-control"},
            ),
            "asset_model": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "DVR MHDX 3116",
                },
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "1",
                    "min": "1",
                },
            ),
            "acquisition_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "placeholder": "Selecione a data de aquisição",
                },
                format="%Y-%m-%d",
            ),
            "invoice_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "NFe 234.980",
                },
            ),
            "supplier": forms.Select(
                attrs={"class": "form-control"},
            ),
            "warranty_expiration_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "requires_maintenance": forms.CheckboxInput(
                attrs={"class": "form-check-input"},
            ),
            "maintenance_frequency": forms.Select(
                attrs={"class": "form-control"},
            ),
            "last_maintenance_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "next_maintenance_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "maintenance_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observações sobre manutenção...",
                },
            ),
            "main_photo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".jpg,.jpeg,.png,.webp",
                },
            ),
            "invoice_file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.jpg,.jpeg,.png",
                },
            ),
            "manual_file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.doc,.docx",
                },
            ),
            "warranty_file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.jpg,.jpeg,.png",
                },
            ),
            "responsible_person": forms.Select(
                attrs={"class": "form-control"},
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"},
            ),
        }

        labels = {
            "condominium": "Condomínio",
            "release_date": "Data de Lançamento",
            "asset_code": "Código do Patrimônio",
            "name": "Nome do Patrimônio",
            "description": "Descrição",
            "asset_type": "Tipo de Patrimônio",
            "asset_category": "Categoria de Patrimônio",
            "location": "Localização",
            "asset_status": "Status do Patrimônio",
            "state_condition": "Estado de Conservação",
            "serial_number": "Número de Série",
            "asset_brand": "Marca do Patrimônio",
            "asset_model": "Modelo",
            "quantity": "Quantidade",
            "acquisition_date": "Data de Aquisição",
            "invoice_number": "Número da Nota Fiscal",
            "supplier": "Entidades",
            "purchase_value": "Valor de Compra",
            "current_value": "Valor Atual",
            "depreciation_rate": "Taxa de Depreciação",
            "useful_life_months": "Vida Útil em Meses",
            "warranty_expiration_date": "Vencimento da Garantia",
            "requires_maintenance": "Requer Manutenção",
            "maintenance_frequency": "Frequência de Manutenção",
            "last_maintenance_date": "Última Manutenção",
            "next_maintenance_date": "Próxima Manutenção",
            "maintenance_notes": "Observações de Manutenção",
            "main_photo": "Foto Principal",
            "invoice_file": "Nota Fiscal",
            "manual_file": "Manual Técnico",
            "warranty_file": "Certificado de Garantia",
            "responsible_person": "Responsável",
            "is_active": "Ativo",
        }

        help_texts = {
            "condominium": "Selecione o condomínio/unidade.",
            "release_date": "Data de lançamento do patrimônio.",
            "asset_code": "Código gerado automaticamente pela ação 'Gerar Código do Patrimônio'.",
            "name": "Informe o nome do patrimônio.",
            "asset_type": "Selecione o tipo de patrimônio.",
            "asset_category": "Selecione a categoria do patrimônio.",
            "asset_status": "Selecione o status do patrimônio.",
            "state_condition": "Selecione o estado de conservação.",
            "location": "Informe a localização física do patrimônio.",
            "purchase_value": "Valor de compra em reais (ex: 2.500,00).",
            "current_value": "Valor atual em reais (ex: 2.100,00).",
            "depreciation_rate": "Taxa de depreciação percentual (ex: 35%).",
            "useful_life_months": "Vida útil em meses (ex: 60).",
            "main_photo": "Formatos aceitos: .jpg, .jpeg, .png, .webp. Máx: 10 MB.",
            "invoice_file": "Formatos aceitos: .pdf, .jpg, .jpeg, .png. Máx: 10 MB.",
            "manual_file": "Formatos aceitos: .pdf, .doc, .docx. Máx: 10 MB.",
            "warranty_file": "Formatos aceitos: .pdf, .jpg, .jpeg, .png. Máx: 10 MB.",
        }

        error_messages = {
            "condominium": {
                "required": "Informe o condomínio/unidade.",
            },
            "release_date": {
                "required": "Informe a data de lançamento.",
                "invalid": "Informe uma data válida.",
            },
            "name": {
                "required": "Informe o nome do patrimônio.",
            },
            "asset_type": {
                "required": "Selecione o tipo de patrimônio.",
            },
            "asset_category": {
                "required": "Selecione a categoria do patrimônio.",
            },
            "asset_status": {
                "required": "Selecione o status do patrimônio.",
            },
            "state_condition": {
                "required": "Selecione o estado de conservação.",
            },
            "quantity": {
                "required": "Informe a quantidade.",
                "invalid": "Informe um número válido.",
                "min_value": "A quantidade mínima é 1.",
            },
            "acquisition_date": {
                "required": "Informe a data de aquisição.",
                "invalid": "Informe uma data válida.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = [
            "release_date",
            "name",
            "asset_type",
            "asset_category",
            "asset_status",
            "state_condition",
            "quantity",
            "acquisition_date",
        ]

        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

    def clean_release_date(self):
        value = self.cleaned_data.get("release_date")
        if value:
            validate_date(value)
        return value

    def clean_quantity(self):
        value = self.cleaned_data.get("quantity")
        if value is not None and value < 1:
            raise forms.ValidationError("A quantidade mínima é 1.")
        return value

    def clean_purchase_value(self):
        value = self.cleaned_data.get("purchase_value")
        if value:
            if isinstance(value, str):
                value = value.replace(".", "").replace(",", ".")
            try:
                return forms.DecimalField(max_digits=12, decimal_places=2).to_python(value)
            except (forms.ValidationError, ValueError, TypeError):
                raise forms.ValidationError("Informe um valor válido.")
        return None

    def clean_current_value(self):
        value = self.cleaned_data.get("current_value")
        if value:
            if isinstance(value, str):
                value = value.replace(".", "").replace(",", ".")
            try:
                return forms.DecimalField(max_digits=12, decimal_places=2).to_python(value)
            except (forms.ValidationError, ValueError, TypeError):
                raise forms.ValidationError("Informe um valor válido.")
        return None

    def clean_depreciation_rate(self):
        value = self.cleaned_data.get("depreciation_rate")
        if value:
            if isinstance(value, str):
                value = value.replace("%", "").replace(",", ".")
            try:
                decimal_val = forms.DecimalField(max_digits=5, decimal_places=2).to_python(value)
            except (forms.ValidationError, ValueError, TypeError):
                raise forms.ValidationError("Informe um percentual válido.")
            if decimal_val < 0 or decimal_val > 100:
                raise forms.ValidationError("O valor deve estar entre 0 e 100.")
            return decimal_val
        return None

    def clean_useful_life_months(self):
        value = self.cleaned_data.get("useful_life_months")
        if not value:
            return None
        try:
            int_val = int(value)
        except (ValueError, TypeError):
            raise forms.ValidationError("Informe um número inteiro válido.")
        if int_val < 1 or int_val > 9999:
            raise forms.ValidationError("O valor deve estar entre 1 e 9999.")
        return int_val

    def clean_main_photo(self):
        file = self.cleaned_data.get("main_photo")
        if file:
            validate_file_size_10mb(file)
            validate_photo_extension(file)
        return file

    def clean_invoice_file(self):
        file = self.cleaned_data.get("invoice_file")
        if file:
            validate_file_size_10mb(file)
            validate_invoice_extension(file)
        return file

    def clean_manual_file(self):
        file = self.cleaned_data.get("manual_file")
        if file:
            validate_file_size_10mb(file)
            validate_manual_extension(file)
        return file

    def clean_warranty_file(self):
        file = self.cleaned_data.get("warranty_file")
        if file:
            validate_file_size_10mb(file)
            validate_warranty_extension(file)
        return file

    def clean(self):
        cleaned_data = super().clean()

        last_maintenance = cleaned_data.get("last_maintenance_date")
        next_maintenance = cleaned_data.get("next_maintenance_date")

        if last_maintenance and next_maintenance and next_maintenance < last_maintenance:
            self.add_error(
                "next_maintenance_date",
                "A próxima manutenção não pode ser anterior à última manutenção.",
            )

        return cleaned_data
