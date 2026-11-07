import re
from datetime import date, datetime

from django import forms
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.formats import number_format

from domains.administrative.models import ChartOfAccount
from domains.financial.exceptions import NewReleaseValidationError
from domains.financial.labels import paymaster_label
from domains.financial.models import NewRelease
from domains.financial.services.newrelease_service import NewReleaseService
from domains.parameters.models.fund_financial import FundFinancial
from domains.residents.models import Resident


class ISODateInput(forms.DateInput):
    """DateInput HTML5 (type=date) com valor no formato AAAA-MM-DD."""

    input_type = "date"

    def __init__(self, attrs=None, format=None):
        super().__init__(attrs=attrs, format=format or "%Y-%m-%d")


class NewReleaseForm(forms.ModelForm):
    """Formulário do módulo 07. Lançamentos."""

    scope = forms.CharField(
        label="Competência",
        max_length=7,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mask-scope",
                "placeholder": "MM-AAAA",
                "inputmode": "numeric",
                "autocomplete": "off",
            }
        ),
        help_text="Informe o mês e o ano no formato MM-AAAA.",
    )

    value = forms.CharField(
        label="Valor",
        required=False,
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mask-currency",
                "placeholder": "0,00",
                "inputmode": "decimal",
                "autocomplete": "off",
            }
        ),
        help_text=(
            "Informe o valor sem o símbolo R$. Débito é armazenado como "
            "negativo e crédito como positivo."
        ),
    )

    class Meta:
        model = NewRelease
        fields = (
            "condominium",
            "paymaster",
            "launchDate",
            "scope",
            "title",
            "chartOfAccounts",
            "fund",
            "launchType",
            "value",
            "notes",
            "is_active",
        )
        widgets = {
            "paymaster": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "255",
                    "placeholder": "Taxa condominial de: MM-AAAA",
                }
            ),
            "launchDate": ISODateInput(attrs={"class": "form-control"}),
            "launchType": forms.RadioSelect(),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observações adicionais",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
        labels = {
            "condominium": "Condomínio/Unidade",
            "paymaster": "Pagador",
            "title": "Título",
            "scope": "Competência",
            "launchDate": "Data do lançamento",
            "chartOfAccounts": "Plano de contas",
            "fund": "Fundo",
            "launchType": "Tipo de lançamento",
            "value": "Valor",
            "notes": "Observações",
            "is_active": "Ativo",
        }
        help_texts = {
            "condominium": "Selecione a unidade condominial do lançamento.",
            "paymaster": "Selecione um morador da unidade escolhida.",
            "title": "Informe um título identificador para o lançamento.",
            "launchDate": "Informe a data efetiva do lançamento.",
            "chartOfAccounts": (
                "Selecione um plano de contas do condomínio da unidade."
            ),
            "fund": "Selecione um fundo do condomínio da unidade.",
            "launchType": (
                "Débito é armazenado como negativo e crédito como positivo."
            ),
            "notes": "Observações adicionais (opcional).",
            "is_active": "Indica se o lançamento está ativo.",
        }
        error_messages = {
            "condominium": {
                "required": "Selecione a unidade do lançamento.",
                "invalid_choice": "Selecione uma unidade válida.",
            },
            "paymaster": {
                "required": "Selecione o pagador do lançamento.",
                "invalid_choice": "Selecione um pagador válido.",
            },
            "title": {
                "required": "Informe o título do lançamento.",
            },
            "launchDate": {
                "required": "Informe a data do lançamento.",
                "invalid": "Informe uma data válida.",
            },
            "chartOfAccounts": {
                "required": "Selecione o plano de contas.",
                "invalid_choice": "Selecione um plano de contas válido.",
            },
            "fund": {
                "required": "Selecione o fundo.",
                "invalid_choice": "Selecione um fundo válido.",
            },
            "launchType": {
                "required": "Selecione o tipo de lançamento.",
                "invalid_choice": "Selecione um tipo de lançamento válido.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        unit_id = None
        if self.is_bound:
            unit_id = self.data.get("condominium")
        if not unit_id and self.instance and self.instance.pk:
            unit_id = self.instance.condominium_id

        selected_paymaster = None
        if self.is_bound:
            selected_paymaster = self.data.get("paymaster")
        elif self.instance and self.instance.pk:
            selected_paymaster = self.instance.paymaster_id

        if unit_id:
            paymaster_filter = Q(unit_id=unit_id, is_active=True)
            if selected_paymaster:
                paymaster_filter |= Q(pk=selected_paymaster)
            paymaster_qs = Resident.objects.filter(paymaster_filter)
        elif selected_paymaster:
            paymaster_qs = Resident.objects.filter(pk=selected_paymaster)
        else:
            paymaster_qs = Resident.objects.none()

        paymaster_field = self.fields["paymaster"]
        paymaster_field.queryset = paymaster_qs.select_related(
            "unit",
            "unit__condominium",
            "type_of_resident",
        ).order_by("name")
        paymaster_field.label_from_instance = paymaster_label
        # No Admin, o widget de FK é envolvido por RelatedFieldWidgetWrapper.
        # O atributo precisa ser gravado no widget interno, pois o wrapper não
        # repassa atributos adicionais para o <select> renderizado.
        paymaster_widget = self.fields["paymaster"].widget
        while hasattr(paymaster_widget, "widget"):
            paymaster_widget = paymaster_widget.widget
        paymaster_widget.attrs["data-residents-url"] = reverse_lazy(
            "admin:financial_newrelease_residents_by_unit"
        )

        self.fields["chartOfAccounts"].queryset = (
            ChartOfAccount.objects.select_related("condominium").all()
        )
        self.fields["fund"].queryset = (
            FundFinancial.objects.select_related("condominium").all()
        )

        if not self.is_bound:
            today = timezone.localdate()
            if not self.initial.get("launchDate"):
                self.initial["launchDate"] = today
            initial_scope = self.initial.get("scope")
            if isinstance(initial_scope, date):
                self.initial["scope"] = initial_scope.strftime("%m-%Y")
            elif not initial_scope:
                self.initial["scope"] = today.strftime("%m-%Y")

            # Em um novo lançamento o Título já vem preenchido com o mesmo
            # texto sugerido no placeholder: "Taxa condominial de: MM-AAAA".
            # Em edição, o título existente é preservado.
            if (
                not (self.instance and self.instance.pk)
                and not self.initial.get("title")
            ):
                self.initial["title"] = (
                    f"Taxa condominial de: {self.initial['scope']}"
                )

        if (
            not self.is_bound
            and self.instance
            and self.instance.pk
            and self.instance.value is not None
        ):
            self.initial["value"] = number_format(
                abs(self.instance.value),
                2,
                force_grouping=True,
            )

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if not title:
            raise forms.ValidationError("Informe o título do lançamento.")
        return title

    def clean_scope(self):
        raw = (self.cleaned_data.get("scope") or "").strip()
        if not re.fullmatch(r"\d{2}-\d{4}", raw):
            raise forms.ValidationError(
                "Informe a competência no formato MM-AAAA."
            )
        try:
            parsed = datetime.strptime(raw, "%m-%Y").date()
        except ValueError as exc:
            raise forms.ValidationError(
                "Informe uma competência válida no formato MM-AAAA."
            ) from exc
        return parsed.replace(day=1)

    def clean_value(self):
        try:
            magnitude = NewReleaseService.parse_value(
                self.cleaned_data.get("value")
            )
        except NewReleaseValidationError as exc:
            raise forms.ValidationError(str(exc))

        if magnitude is None:
            return None

        try:
            return NewReleaseService.apply_sign(
                magnitude,
                self.cleaned_data.get("launchType"),
            )
        except NewReleaseValidationError as exc:
            raise forms.ValidationError(str(exc))

    def clean(self):
        cleaned_data = super().clean()
        unit = cleaned_data.get("condominium")
        paymaster = cleaned_data.get("paymaster")
        chart_of_accounts = cleaned_data.get("chartOfAccounts")
        fund = cleaned_data.get("fund")

        if unit and paymaster and paymaster.unit_id != unit.pk:
            self.add_error(
                "paymaster",
                "O pagador deve pertencer à unidade selecionada.",
            )

        if (
            unit
            and chart_of_accounts
            and chart_of_accounts.condominium_id != unit.condominium_id
        ):
            self.add_error(
                "chartOfAccounts",
                "O plano de contas deve pertencer ao condomínio da unidade "
                "selecionada.",
            )

        if (
            unit
            and fund
            and fund.condominium_id != unit.condominium_id
        ):
            self.add_error(
                "fund",
                "O fundo deve pertencer ao condomínio da unidade selecionada.",
            )

        return cleaned_data
