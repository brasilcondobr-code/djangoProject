import re
from datetime import date, datetime
from decimal import Decimal

from django import forms
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.formats import number_format

from domains.administrative.models import ChartOfAccount
from domains.financial.exceptions import (
    CollectionValidationError,
    NewReleaseValidationError,
)
from domains.financial.labels import paymaster_label
from domains.financial.models import Collection, CollectionCredit, NewRelease
from domains.financial.repositories import FinancialRepository
from domains.financial.services.collection_service import CollectionService
from domains.financial.services.newrelease_service import NewReleaseService
from domains.parameters.models import FinancialTransaction
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
            "Informe o valor sem o símbolo R$. Débito aparece como positivo "
            "e crédito como negativo."
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
                "Débito é armazenado como positivo e crédito como negativo."
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
                self.instance.value,
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


class CollectionForm(forms.ModelForm):
    """Formulário do módulo 04. Cobranças."""

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

    originalValue = forms.CharField(
        label="Valor original",
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
        help_text="Informe o valor sem o símbolo R$.",
    )

    discountPercent = forms.CharField(
        label="% Desconto",
        required=False,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mask-percent",
                "placeholder": "0,00",
                "inputmode": "decimal",
                "autocomplete": "off",
            }
        ),
        help_text="Percentual entre 0 e 100.",
    )

    penaltyPercent = forms.CharField(
        label="% Multa",
        required=False,
        max_length=8,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mask-percent",
                "placeholder": "0,00",
                "inputmode": "decimal",
                "autocomplete": "off",
            }
        ),
        help_text="Percentual entre 0 e 100.",
    )

    feesPercent = forms.CharField(
        label="% Juros",
        required=False,
        max_length=8,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mask-percent",
                "placeholder": "0,00",
                "inputmode": "decimal",
                "autocomplete": "off",
            }
        ),
        help_text="Percentual entre 0 e 100.",
    )

    chargesPercent = forms.CharField(
        label="% Encargos",
        required=False,
        max_length=8,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mask-percent",
                "placeholder": "0,00",
                "inputmode": "decimal",
                "autocomplete": "off",
            }
        ),
        help_text="Percentual entre 0 e 100.",
    )

    class Meta:
        model = Collection
        fields = (
            "condominium",
            "scope",
            "originalValue",
            "discountPercent",
            "penaltyPercent",
            "feesPercent",
            "chargesPercent",
            "discountDeadline",
            "dueDate",
            "is_active",
        )
        widgets = {
            "condominium": forms.Select(attrs={"class": "form-control"}),
            "discountDeadline": ISODateInput(attrs={"class": "form-control"}),
            "dueDate": ISODateInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
        labels = {
            "condominium": "Condomínio/Unidade",
            "discountDeadline": "Data limite para desconto",
            "dueDate": "Data de vencimento",
            "is_active": "Ativo",
        }
        help_texts = {
            "condominium": "Selecione a unidade condominial da cobrança.",
            "discountDeadline": (
                "Informe a data limite para aplicação do desconto."
            ),
            "dueDate": "Informe a data de vencimento da cobrança.",
            "is_active": "Indica se a cobrança está ativa.",
        }
        error_messages = {
            "condominium": {
                "required": "Selecione a unidade da cobrança.",
                "invalid_choice": "Selecione uma unidade válida.",
            },
            "discountDeadline": {
                "required": "Informe a data limite para desconto.",
                "invalid": "Informe uma data válida.",
            },
            "dueDate": {
                "required": "Informe a data de vencimento.",
                "invalid": "Informe uma data válida.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = timezone.localdate()
        if (
            self.instance
            and not self.instance.pk
            and not self.instance.billingDate
        ):
            # Exibe a data atual no formulário de inclusão. O valor
            # definitivo continua sendo gravado pelo servidor no save.
            self.instance.billingDate = today

        if self.is_bound:
            return

        if self.instance and self.instance.pk:
            if self.instance.scope:
                self.initial["scope"] = self.instance.scope.strftime("%m-%Y")
            for field in (
                "originalValue",
                "discountPercent",
                "penaltyPercent",
                "feesPercent",
                "chargesPercent",
            ):
                value = getattr(self.instance, field, None)
                if value is not None:
                    self.initial[field] = number_format(
                        value, 2, force_grouping=True
                    )
        else:
            self.initial["scope"] = today.strftime("%m-%Y")

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

    def _clean_money(self, field, label):
        try:
            return CollectionService.parse_money(
                self.cleaned_data.get(field),
                label=label,
            )
        except CollectionValidationError as exc:
            raise forms.ValidationError(str(exc))

    def _clean_percent(self, field, label):
        try:
            return CollectionService.parse_percent(
                self.cleaned_data.get(field),
                label=label,
            )
        except CollectionValidationError as exc:
            raise forms.ValidationError(str(exc))

    def clean_originalValue(self):
        return self._clean_money("originalValue", "valor original")

    def clean_discountPercent(self):
        return self._clean_percent("discountPercent", "% desconto")

    def clean_penaltyPercent(self):
        return self._clean_percent("penaltyPercent", "% multa")

    def clean_feesPercent(self):
        return self._clean_percent("feesPercent", "% juros")

    def clean_chargesPercent(self):
        return self._clean_percent("chargesPercent", "% encargos")

    def clean(self):
        cleaned_data = super().clean()
        unit = cleaned_data.get("condominium")
        scope = cleaned_data.get("scope")
        due_date = cleaned_data.get("dueDate")

        billing_date = (
            self.instance.billingDate
            if self.instance and self.instance.pk
            else timezone.localdate()
        )

        if unit and scope and due_date and billing_date:
            duplicates = Collection.objects.filter(
                condominium=unit,
                billingDate=billing_date,
                scope=scope,
                dueDate=due_date,
            )
            if self.instance and self.instance.pk:
                duplicates = duplicates.exclude(pk=self.instance.pk)
            if duplicates.exists():
                self.add_error(
                    None,
                    "Já existe uma cobrança para esta unidade, data de "
                    "cobrança, competência e vencimento.",
                )

        self._refresh_calculated_values(cleaned_data)

        return cleaned_data

    def _refresh_calculated_values(self, cleaned_data):
        """Mantém total e saldo coerentes na apresentação do formulário.

        O valor definitivo é recalculado pelo ``CollectionService`` no
        momento da gravação; aqui apenas evitamos que a tela reexibida após
        um erro mostre total e saldo divergentes.
        """
        original = cleaned_data.get("originalValue")
        if original is None:
            return

        value_fields = (
            "originalValue",
            "discountPercent",
            "penaltyPercent",
            "feesPercent",
            "chargesPercent",
        )
        if any(field in self.errors for field in value_fields):
            return

        amounts = CollectionService.calculate_amounts(
            original,
            discount_percent=cleaned_data.get("discountPercent"),
            penalty_percent=cleaned_data.get("penaltyPercent"),
            fees_percent=cleaned_data.get("feesPercent"),
            charges_percent=cleaned_data.get("chargesPercent"),
        )

        for field, value in amounts.items():
            setattr(self.instance, field, value)

        received = (
            CollectionService.received_total(self.instance.pk)
            if self.instance.pk
            else CollectionService.ZERO
        )
        self.instance.balance = CollectionService.calculate_balance(
            amounts["totalAmount"],
            received,
        )


class CollectionPaymentForm(forms.Form):
    """Formulário da ação Pagamento (página intermediária)."""

    collection = forms.ModelChoiceField(
        label="Cobrança",
        queryset=Collection.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    financialTransaction = forms.ModelChoiceField(
        label="Operação financeira",
        queryset=FinancialTransaction.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    dateReceived = forms.DateField(
        label="Data de recebimento",
        widget=ISODateInput(attrs={"class": "form-control"}),
    )
    amountReceived = forms.CharField(
        label="Valor recebido",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mask-currency",
                "placeholder": "0,00",
                "inputmode": "decimal",
                "autocomplete": "off",
            }
        ),
    )

    def __init__(self, *args, collections=None, **kwargs):
        super().__init__(*args, **kwargs)
        if collections is not None:
            self.fields["collection"].queryset = collections
        if not self.is_bound and not self.initial.get("dateReceived"):
            self.initial["dateReceived"] = timezone.localdate()

    def clean_amountReceived(self):
        try:
            return CollectionService.parse_money(
                self.cleaned_data.get("amountReceived"),
                label="valor recebido",
                required=True,
            )
        except CollectionValidationError as exc:
            raise forms.ValidationError(str(exc))

    def clean(self):
        cleaned_data = super().clean()
        collection = cleaned_data.get("collection")
        amount = cleaned_data.get("amountReceived")

        if collection is not None and amount is not None:
            available = CollectionService.available_balance(collection)
            if amount > available:
                self.add_error(
                    "amountReceived",
                    "O valor recebido excede o saldo disponível de "
                    f"R$ {available:.2f}.",
                )

        return cleaned_data


class CollectionCreditForm(forms.ModelForm):
    """Formulário do inline de créditos da cobrança."""

    amountCredit = forms.CharField(
        label="Valor do crédito",
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
    )

    class Meta:
        model = CollectionCredit
        fields = ("financialTransaction", "creditDate", "amountCredit")
        widgets = {
            "financialTransaction": forms.Select(
                attrs={"class": "form-control"}
            ),
            "creditDate": ISODateInput(attrs={"class": "form-control"}),
        }
        labels = {
            "financialTransaction": "Operação financeira",
            "creditDate": "Data do crédito",
            "amountCredit": "Valor do crédito",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        transactions = FinancialTransaction.objects.filter(is_active=True)
        if (
            self.instance
            and self.instance.pk
            and self.instance.financialTransaction_id
        ):
            transactions = FinancialTransaction.objects.filter(
                Q(is_active=True)
                | Q(pk=self.instance.financialTransaction_id)
            )
        self.fields["financialTransaction"].queryset = transactions
        # A cobrança pode ser lançada antes do crédito/pagamento existir.
        # Os campos só são exigidos quando a linha é efetivamente preenchida.
        self.fields["financialTransaction"].required = False
        if not self.is_bound:
            if not self.initial.get("creditDate"):
                self.initial["creditDate"] = timezone.localdate()
            if (
                self.instance
                and self.instance.pk
                and self.instance.amountCredit is not None
            ):
                self.initial["amountCredit"] = number_format(
                    self.instance.amountCredit,
                    2,
                    force_grouping=True,
                )

    def has_changed(self):
        """Considera vazia a linha sem operação e sem valor.

        A data do crédito já vem preenchida com a data atual, então uma
        linha intocada não pode ser tratada como preenchida apenas por
        causa dela.
        """
        if not super().has_changed():
            return False

        return bool(
            self.data.get(self.add_prefix("financialTransaction"))
            or self.data.get(self.add_prefix("amountCredit"))
        )

    def clean_amountCredit(self):
        try:
            return CollectionService.parse_money(
                self.cleaned_data.get("amountCredit"),
                label="valor do crédito",
                required=False,
            )
        except CollectionValidationError as exc:
            raise forms.ValidationError(str(exc))

    def clean(self):
        cleaned_data = super().clean()

        operation = cleaned_data.get("financialTransaction")
        amount = cleaned_data.get("amountCredit")
        credit_date = cleaned_data.get("creditDate")

        if operation is None and amount is None:
            # Linha não preenchida: o crédito será registrado depois do
            # lançamento da cobrança.
            return cleaned_data

        if operation is None and "financialTransaction" not in self.errors:
            self.add_error(
                "financialTransaction",
                "Selecione a operação financeira do crédito.",
            )
        if amount is None and "amountCredit" not in self.errors:
            self.add_error(
                "amountCredit",
                "Informe o valor do crédito.",
            )
        if credit_date is None and "creditDate" not in self.errors:
            self.add_error(
                "creditDate",
                "Informe a data do crédito.",
            )

        return cleaned_data


class CollectionCreditFormSet(forms.BaseInlineFormSet):
    """Valida a soma dos créditos contra o saldo antes de persistir."""

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        collection = self.instance
        if not collection:
            return

        total_credits = CollectionService.ZERO
        for form in self.forms:
            if not form.cleaned_data:
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            amount = form.cleaned_data.get("amountCredit")
            if amount:
                total_credits += amount

        if total_credits <= 0:
            return

        total_amount = collection.totalAmount
        if collection.originalValue is not None:
            # O formulário principal pode ter alterado os valores; nesse
            # caso o total em memória ainda é o persistido. Recalcula para
            # validar os créditos contra o total efetivamente submetido.
            try:
                amounts = CollectionService.calculate_amounts(
                    CollectionService.parse_money(
                        collection.originalValue,
                        label="valor original",
                    ),
                    discount_percent=collection.discountPercent,
                    penalty_percent=collection.penaltyPercent,
                    fees_percent=collection.feesPercent,
                    charges_percent=collection.chargesPercent,
                )
            except CollectionValidationError:
                return
            total_amount = amounts["totalAmount"]
        else:
            total_amount = None

        if total_amount is None:
            raise forms.ValidationError(
                "A cobrança não possui valor total para receber créditos."
            )

        payments_total = Decimal(
            FinancialRepository.get_collection_payments_total(
                collection.pk
            )
            or 0
        ) if collection.pk else CollectionService.ZERO
        available = Decimal(total_amount) - payments_total

        if total_credits > available:
            raise forms.ValidationError(
                "A soma dos créditos excede o saldo disponível de "
                f"R$ {max(available, CollectionService.ZERO):.2f}."
            )
