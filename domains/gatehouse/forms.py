from django import forms
from django.db.models import Q

from domains.condominium.models import Collaborator, Condominium
from domains.gatehouse.models import ServiceTransition, ServiceTransitionObject, Shift, ShiftScale
from domains.parameters.models import ConciergeServiceCategory

SELECT_ATTRS = {
    "class": "servicetransition-select",
    "style": (
        "color: #212529 !important; background-color: #ffffff !important; "
        "border: 1px solid #ced4da !important;"
    ),
}


class ISODateInput(forms.DateInput):
    """DateInput HTML5 (type=date) que emite o value em ISO (YYYY-MM-DD).

    O DateInput padrao localiza a data (pt-BR: dd/mm/yyyy); o navegador ignora
    esse valor em <input type="date">, que exige ISO — resultando em campo
    vazio na tela e envio vazio no POST.
    """

    def format_value(self, value):
        if value in (None, ""):
            return None
        if isinstance(value, str):
            return value
        isoformat = getattr(value, "isoformat", None)
        if callable(isoformat):
            return isoformat()
        return super().format_value(value)


def active_queryset(model, instance, field_name, order_by="name"):
    """Queryset ordenado, sem inativos, preservando o registro selecionado na edição."""
    qs = model._default_manager.all()
    selected_pk = getattr(instance, "%s_id" % field_name, None)
    if selected_pk:
        qs = qs.filter(Q(is_active=True) | Q(pk=selected_pk))
    else:
        qs = qs.filter(is_active=True)
    return qs.order_by(order_by)


class ServiceTransitionForm(forms.ModelForm):
    """Formulário principal da passagem de serviço (02)."""

    class Meta:
        model = ServiceTransition
        fields = ("condominium", "collaboratorEnd", "collaboratorStart", "releaseDate", "observations")
        widgets = {
            "condominium": forms.Select(attrs=SELECT_ATTRS),
            "collaboratorEnd": forms.Select(attrs=SELECT_ATTRS),
            "collaboratorStart": forms.Select(attrs=SELECT_ATTRS),
            "releaseDate": ISODateInput(attrs={"type": "date"}),
            "observations": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Observações da passagem de serviço"},
            ),
        }
        help_texts = {
            "condominium": "Condomínio da passagem de serviço",
            "collaboratorEnd": "Colaborador que está saindo do turno",
            "collaboratorStart": "Colaborador que está entrando no turno",
            "releaseDate": "Data de lançamento da passagem",
            "observations": "Observações adicionais (opcional)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["condominium"].queryset = active_queryset(
            Condominium, self.instance, "condominium"
        )
        self.fields["collaboratorEnd"].queryset = active_queryset(
            Collaborator, self.instance, "collaboratorEnd"
        )
        self.fields["collaboratorStart"].queryset = active_queryset(
            Collaborator, self.instance, "collaboratorStart"
        )


class ServiceTransitionObjectForm(forms.ModelForm):
    """Formulário de cada objeto vinculado à passagem de serviço."""

    amountObj = forms.IntegerField(
        label="Quantidade",
        min_value=1,
        initial=1,
        help_text="Quantidade do item (mínimo 1)",
        widget=forms.NumberInput(attrs={"min": 1, "step": 1, "placeholder": "1"}),
    )

    class Meta:
        model = ServiceTransitionObject
        fields = ("categoryObj", "itemObj", "amountObj", "shiftDate")
        widgets = {
            "categoryObj": forms.Select(attrs=SELECT_ATTRS),
            "itemObj": forms.TextInput(attrs={"placeholder": "Nome do item"}),
            "shiftDate": ISODateInput(attrs={"type": "date"}),
        }
        help_texts = {
            "categoryObj": "Categoria do objeto",
            "itemObj": "Nome do item",
            "shiftDate": "Data do turno (padrão: data atual)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoryObj"].queryset = active_queryset(
            ConciergeServiceCategory, self.instance, "categoryObj", order_by="description"
        )


class ShiftScaleForm(forms.Form):
    """Formulário para uma escala individual."""

    description = forms.CharField(
        label="Descrição",
        max_length=255,
        required=False,
        help_text="Descrição da escala",
    )
    shiftDate = forms.DateField(
        label="Data do Plantão",
        help_text="Data da escala",
        widget=ISODateInput(attrs={"type": "date"}),
    )
    startTime = forms.TimeField(
        label="Hora Inicial",
        help_text="Hora inicial da escala",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    endTime = forms.TimeField(
        label="Hora Final",
        help_text="Hora final da escala",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    is_active = forms.BooleanField(
        label="Ativo",
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
            "startDate": ISODateInput(attrs={"type": "date"}),
            "endDate": ISODateInput(attrs={"type": "date"}),
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
