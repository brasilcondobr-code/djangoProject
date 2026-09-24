from django import forms
from domains.gatehouse.models import Shift, ShiftScale


class ShiftScaleForm(forms.Form):
    """Formulário para uma escala individual."""

    description = forms.CharField(
        "Descrição",
        max_length=255,
        required=False,
        help_text="Descrição da escala",
    )
    shiftDate = forms.DateField(
        "Data do Plantão",
        help_text="Data da escala",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    startTime = forms.TimeField(
        "Hora Inicial",
        help_text="Hora inicial da escala",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    endTime = forms.TimeField(
        "Hora Final",
        help_text="Hora final da escala",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    is_active = forms.BooleanField(
        "Ativo",
        initial=True,
        required=False,
    )


class ShiftForm(forms.ModelForm):
    """Formulário principal para o plantão."""

    class Meta:
        model = Shift
        fields = (
            "condominium",
            "collaborator",
            "startDate",
            "endDate",
            "title",
            "status",
            "is_active",
        )
        widgets = {
            "startDate": forms.DateInput(attrs={"type": "date"}),
            "endDate": forms.DateInput(attrs={"type": "date"}),
            "title": forms.TextInput(attrs={"placeholder": "Título do plantão"}),
        }
        help_texts = {
            "condominium": "Condomínio associado ao plantão",
            "collaborator": "Colaborador do plantão",
            "startDate": "Data inicial do plantão",
            "endDate": "Data final do plantão",
            "title": "Título do plantão (opcional)",
            "status": "Status do plantão",
            "is_active": "Indica se o plantão está ativo",
        }

    def clean(self):
        """Validações cruzadas no formulário."""
        cleaned_data = super().clean()
        startDate = cleaned_data.get("startDate")
        endDate = cleaned_data.get("endDate")

        if startDate and endDate and startDate > endDate:
            raise forms.ValidationError(
                "A data final deve ser maior ou igual à data inicial."
            )

        return cleaned_data
