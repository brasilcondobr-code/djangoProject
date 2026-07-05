from django import forms
from domains.administrative.models.meters import Meters
from domains.administrative.validators.validators import (
    validate_meter_composition,
    validate_meter_file_extension,
)
from core.services.validators import validate_date

class MetersForm(forms.ModelForm):
    previousValue = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control js-mask-decimal", "placeholder": "0,000"}),
        label="Valor Anterior"
    )
    currentValue = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control js-mask-decimal", "placeholder": "0,000"}),
        label="Valor Atual"
    )
    Consumption = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control js-mask-decimal", "placeholder": "0,000"}),
        label="Consumo"
    )
    Value = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control js-mask-decimal", "placeholder": "0,00"}),
        label="Valor"
    )

    class Meta:
        model = Meters
        fields = "__all__"

        widgets = {
            "condominium": forms.Select(
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
            "meterType": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "composition": forms.TextInput(
                attrs={
                    "class": "form-control js-mask-composition",
                    "placeholder": "MM/AAAA",
                    "maxlength": "7",
                    "autocomplete": "off",
                }
            ),
            "file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".jpg,.jpeg,.png,.bmp",
                }
            ),
        }

        labels = {
            "condominium": "Condomínio/Unidade",
            "releaseDate": "Data de Lançamento",
            "meterType": "Tipo de Medidor",
            "composition": "Composição",
            "file": "Arquivo do Documento",
            "is_active": "Ativo",
        }

        help_texts = {
            "condominium": "Selecione o condomínio.",
            "releaseDate": "Selecione a data de lançamento da leitura.",
            "meterType": "Selecione o tipo de medidor.",
            "unit_identification": "Selecione a unidade da leitura.",
            "composition": "Informe a competência no formato MM/AAAA.",
            "previousValue": "Informe o valor anterior do medidor, se houver.",
            "currentValue": "Informe o valor atual do medidor, se houver.",
            "Consumption": "Informe o consumo ou deixe que o sistema calcule quando possível.",
            "Value": "Informe o valor financeiro do consumo.",
            "file": "Obrigatório. Formatos aceitos: .jpg, .jpeg, .png e .bmp.",
        }

        error_messages = {
            "condominium": {
                "required": "O condomínio é obrigatório.",
            },
            "releaseDate": {
                "required": "A data de lançamento é obrigatória.",
                "invalid": "Informe uma data válida.",
            },
            "meterType": {
                "required": "O tipo de medidor é obrigatório.",
            },
            "unit_identification": {
                "required": "A unidade é obrigatória.",
            },
            "composition": {
                "required": "A composição é obrigatória.",
            },
            "Consumption": {
                "required": "O consumo é obrigatório.",
                "invalid": "Informe um consumo válido.",
            },
            "Value": {
                "required": "O valor é obrigatório.",
                "invalid": "Informe um valor válido.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = [
            "condominium",
            "releaseDate",
            "meterType",
            "composition",
            "Consumption",
            "Value",
        ]

        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

        optional_fields = [
            "previousValue",
            "currentValue",
        ]

        for field_name in optional_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False


    def clean_releaseDate(self):
        release_date = self.cleaned_data.get("releaseDate")

        if not release_date:
            raise forms.ValidationError("A data de lançamento é obrigatória.")

        validate_date(release_date)

        return release_date

    def clean_composition(self):
        composition = self.cleaned_data.get("composition")

        validate_meter_composition(composition)

        return composition

    def clean_previousValue(self):
        value = self.cleaned_data.get("previousValue")
        if value is not None:
            if isinstance(value, str):
                value = value.replace(",", ".")
            try:
                return forms.DecimalField().to_python(value)
            except (ValidationError, ValueError, TypeError):
                raise forms.ValidationError("Informe um número.")
        return value

    def clean_currentValue(self):
        value = self.cleaned_data.get("currentValue")
        if value is not None:
            if isinstance(value, str):
                value = value.replace(",", ".")
            try:
                return forms.DecimalField().to_python(value)
            except (ValidationError, ValueError, TypeError):
                raise forms.ValidationError("Informe um número.")
        return value

    def clean_Consumption(self):
        value = self.cleaned_data.get("Consumption")
        if value is not None:
            if isinstance(value, str):
                value = value.replace(",", ".")
            try:
                return forms.DecimalField().to_python(value)
            except (ValidationError, ValueError, TypeError):
                raise forms.ValidationError("Informe um consumo válido.")
        return value

    def clean_Value(self):
        value = self.cleaned_data.get("Value")
        if value is not None:
            if isinstance(value, str):
                value = value.replace(",", ".")
            try:
                return forms.DecimalField().to_python(value)
            except (ValidationError, ValueError, TypeError):
                raise forms.ValidationError("Informe um valor válido.")
        return value

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if not file:
            return None
        validate_meter_file_extension(file)
        return file

    def clean(self):
        cleaned_data = super().clean()

        previous_value = cleaned_data.get("previousValue")
        current_value = cleaned_data.get("currentValue")
        consumption = cleaned_data.get("Consumption")
        value = cleaned_data.get("Value")

        if previous_value is not None and previous_value < 0:
            self.add_error(
                "previousValue",
                "O valor anterior não pode ser negativo.",
            )

        if current_value is not None and current_value < 0:
            self.add_error(
                "currentValue",
                "O valor atual não pode ser negativo.",
            )

        if (
            previous_value is not None
            and current_value is not None
            and current_value < previous_value
        ):
            self.add_error(
                "currentValue",
                "O valor atual não pode ser menor que o valor anterior.",
            )

        if consumption is None:
            self.add_error(
                "Consumption",
                "O consumo é obrigatório.",
            )
        elif consumption < 0:
            self.add_error(
                "Consumption",
                "O consumo não pode ser negativo.",
            )

        if value is None:
            self.add_error(
                "Value",
                "O valor é obrigatório.",
            )
        elif value < 0:
            self.add_error(
                "Value",
                "O valor não pode ser negativo.",
            )

        return cleaned_data
