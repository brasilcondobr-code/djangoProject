"""Formulário do módulo 01. Locações.

As regras de negócio obrigatórias ficam no servidor (service). O formulário
faz validações imediatas e amigáveis, incluindo a checagem de capacidade para
exibir o erro no próprio formulário do Admin.
"""

from django import forms
from django.db import connection, models

from domains.reservations.exceptions import (
    MaintenanceReservationValidationError,
    RentalError,
    RentalValidationError,
)
from domains.reservations.models import MaintenanceReservations, Rentals
from domains.reservations.repositories import ReservationsRepository
from domains.reservations.services.maintenance_reservations_service import (
    MaintenanceReservationsService,
)
from domains.reservations.services.rentals_service import RentalsService
from domains.reservations.validators import (
    normalize_applicant,
    parse_rental_price,
    validate_period,
    validate_price,
)
from domains.reservations.validators.maintenance_reservations_validators import (
    normalize_applicant as normalize_maintenance_applicant,
    validate_period as validate_maintenance_period,
)
from domains.parameters.models import (
    TypesOfMaintenanceReservations,
    TypesOfRental,
)
from domains.residents.models import CondominiumUnit


class ISODateInput(forms.DateInput):
    """``<input type="date">`` com value em ISO (YYYY-MM-DD).

    O widget padrão localiza a data (dd/mm/aaaa), que o navegador ignora em
    ``type=date``. Mesmo padrão adotado no app gatehouse.
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


class RentalsForm(forms.ModelForm):
    # Declarado como CharField para aceitar o formato pt-BR (ex.: 1.234,56).
    # A máscara no navegador é apenas visual; a conversão é feita aqui e a
    # validação definitiva fica nos validadores do domínio.
    rentalPrice = forms.CharField(
        label="Valor da locação",
        required=False,
        max_length=20,
        help_text=(
            "Obrigatório e maior que zero quando a cobrança estiver "
            "habilitada."
        ),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "0,00",
                "inputmode": "decimal",
                "autocomplete": "off",
            }
        ),
    )

    class Meta:
        model = Rentals
        fields = (
            "condominium",
            "typesOfRentals",
            "startDate",
            "endDate",
            "applicant",
            "rentalPrice",
            "charge_amount",
            "observations",
            "is_active",
        )
        widgets = {
            "condominium": forms.Select(attrs={"class": "form-control"}),
            "typesOfRentals": forms.Select(attrs={"class": "form-control"}),
            "startDate": ISODateInput(attrs={"type": "date"}),
            "endDate": ISODateInput(attrs={"type": "date"}),
            "applicant": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome do solicitante",
                    "maxlength": "255",
                }
            ),
            "charge_amount": forms.RadioSelect(
                choices=((True, "Sim"), (False, "Não"))
            ),
            "observations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observações (opcional)",
                }
            ),
        }
        labels = {
            "condominium": "Unidade",
            "typesOfRentals": "Tipo de locação",
            "startDate": "Data inicial",
            "endDate": "Data final",
            "applicant": "Solicitante",
            "charge_amount": "Cobrar valor?",
            "observations": "Observações",
            "is_active": "Ativo",
        }
        help_texts = {
            "condominium": "Unidade condominial da locação.",
            "typesOfRentals": (
                "Tipo de locação que define os limites de agendamentos e "
                "reservas."
            ),
            "startDate": "Data inicial da locação (inclusive).",
            "endDate": (
                "Data final da locação (inclusive); deve ser maior ou igual "
                "à data inicial."
            ),
            "applicant": "Nome do solicitante (até 255 caracteres).",
            "charge_amount": (
                "Quando 'Não', o valor da locação é limpo ao salvar."
            ),
            "observations": "Observações sobre a locação (opcional).",
            "is_active": "Locações inativas não entram no controle de capacidade.",
        }
        error_messages = {
            "condominium": {"required": "Selecione a unidade da locação."},
            "typesOfRentals": {
                "required": "Selecione o tipo de locação."
            },
            "startDate": {"required": "Informe a data inicial."},
            "endDate": {"required": "Informe a data final."},
            "applicant": {"required": "Informe o solicitante."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "condominium" in self.fields:
            self.fields["condominium"].queryset = (
                CondominiumUnit.objects.select_related("condominium").order_by(
                    "condominium__name", "tower", "unit_number"
                )
            )

        if "typesOfRentals" in self.fields:
            queryset = TypesOfRental.objects.all()
            if self.instance.pk and self.instance.typesOfRentals_id:
                queryset = queryset.filter(
                    models.Q(is_active=True)
                    | models.Q(pk=self.instance.typesOfRentals_id)
                )
            else:
                queryset = queryset.filter(is_active=True)
            self.fields["typesOfRentals"].queryset = queryset.order_by(
                "description"
            )

    # ------------------------------------------------------------------
    # Campos
    # ------------------------------------------------------------------
    def clean_applicant(self):
        try:
            return normalize_applicant(self.cleaned_data.get("applicant"))
        except RentalValidationError as exc:
            raise forms.ValidationError(str(exc))

    def clean_rentalPrice(self):
        try:
            return parse_rental_price(self.cleaned_data.get("rentalPrice"))
        except RentalValidationError as exc:
            raise forms.ValidationError(str(exc))

    # ------------------------------------------------------------------
    # Validação cruzada
    # ------------------------------------------------------------------
    def clean(self):
        cleaned_data = super().clean()

        if self.instance.pk:
            if self.instance.status != Rentals.Status.AGENDAMENTO:
                raise forms.ValidationError(
                    "Somente locações em Agendamento podem ser editadas."
                )
            # Revalida o status sob lock: uma ação em lote pode ter alterado o
            # registro entre a renderização e o POST.
            if connection.in_atomic_block:
                try:
                    locked = ReservationsRepository.get_rental_for_update(
                        self.instance.pk
                    )
                except Rentals.DoesNotExist:
                    raise forms.ValidationError("Locação não encontrada.")
                if locked.status != Rentals.Status.AGENDAMENTO:
                    raise forms.ValidationError(
                        "Somente locações em Agendamento podem ser editadas. "
                        f"Status atual: '{locked.get_status_display()}'."
                    )

        start_date = cleaned_data.get("startDate")
        end_date = cleaned_data.get("endDate")
        if start_date and end_date:
            try:
                validate_period(start_date, end_date)
            except RentalValidationError as exc:
                self.add_error("endDate", str(exc))

        charge_amount = cleaned_data.get("charge_amount")
        if charge_amount is None:
            charge_amount = True
        price_field_has_error = "rentalPrice" in self.errors
        if "rentalPrice" in cleaned_data:
            try:
                cleaned_data["rentalPrice"] = validate_price(
                    charge_amount, cleaned_data.get("rentalPrice")
                )
            except RentalValidationError as exc:
                self.add_error("rentalPrice", str(exc))
        elif not charge_amount:
            # Campo não enviado (ex.: input desabilitado pelo JS ao escolher
            # "Não"): o preço é limpo no servidor, sem depender do navegador.
            cleaned_data["rentalPrice"] = None
        elif not price_field_has_error:
            self.add_error(
                "rentalPrice",
                "Informe o valor da locação quando a cobrança estiver "
                "habilitada.",
            )

        unit = cleaned_data.get("condominium")
        rental_type = cleaned_data.get("typesOfRentals")
        if self.errors or not (unit and rental_type and start_date and end_date):
            return cleaned_data

        probe = Rentals(
            pk=self.instance.pk,
            condominium=unit,
            typesOfRentals=rental_type,
            startDate=start_date,
            endDate=end_date,
            charge_amount=charge_amount,
            rentalPrice=cleaned_data.get("rentalPrice"),
        )
        try:
            RentalsService.assert_capacity_for_form(probe)
        except RentalError as exc:
            raise forms.ValidationError(str(exc))

        return cleaned_data


class MaintenanceReservationsForm(forms.ModelForm):
    """Formulário do módulo 02. Manutenções.

    As regras de domínio (status, transições e auditoria) ficam no service.
    Aqui ficam apenas validações imediatas e mensagens amigáveis.
    """

    class Meta:
        model = MaintenanceReservations
        fields = (
            "condominium",
            "typesOfMaintenance",
            "startDate",
            "endDate",
            "applicant",
            "observations",
            "is_active",
        )
        widgets = {
            "condominium": forms.Select(attrs={"class": "form-control"}),
            "typesOfMaintenance": forms.Select(
                attrs={"class": "form-control"}
            ),
            "startDate": ISODateInput(attrs={"type": "date"}),
            "endDate": ISODateInput(attrs={"type": "date"}),
            "applicant": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome do solicitante",
                    "maxlength": "255",
                }
            ),
            "observations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observações (opcional)",
                }
            ),
        }
        labels = {
            "condominium": "Unidade",
            "typesOfMaintenance": "Tipo de manutenção",
            "startDate": "Data inicial",
            "endDate": "Data final",
            "applicant": "Solicitante",
            "observations": "Observações",
            "is_active": "Ativo",
        }
        help_texts = {
            "condominium": "Unidade condominial da manutenção.",
            "typesOfMaintenance": "Tipo que classifica a manutenção.",
            "startDate": "Data inicial da manutenção (inclusive).",
            "endDate": (
                "Data final da manutenção (inclusive); deve ser maior ou "
                "igual à data inicial."
            ),
            "applicant": "Nome do solicitante (até 255 caracteres).",
            "observations": "Observações sobre a manutenção (opcional).",
            "is_active": "Define se a manutenção está ativa.",
        }
        error_messages = {
            "condominium": {"required": "Selecione a unidade da manutenção."},
            "typesOfMaintenance": {
                "required": "Selecione o tipo de manutenção."
            },
            "startDate": {"required": "Informe a data inicial."},
            "endDate": {"required": "Informe a data final."},
            "applicant": {"required": "Informe o solicitante."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "condominium" in self.fields:
            self.fields["condominium"].queryset = (
                CondominiumUnit.objects.select_related("condominium").order_by(
                    "condominium__name", "tower", "unit_number"
                )
            )

        if "typesOfMaintenance" in self.fields:
            queryset = TypesOfMaintenanceReservations.objects.all()
            if self.instance.pk and self.instance.typesOfMaintenance_id:
                queryset = queryset.filter(
                    models.Q(is_active=True)
                    | models.Q(pk=self.instance.typesOfMaintenance_id)
                )
            else:
                queryset = queryset.filter(is_active=True)
            self.fields["typesOfMaintenance"].queryset = queryset.order_by(
                "description"
            )

    # ------------------------------------------------------------------
    # Campos
    # ------------------------------------------------------------------
    def clean_applicant(self):
        try:
            return normalize_maintenance_applicant(
                self.cleaned_data.get("applicant")
            )
        except MaintenanceReservationValidationError as exc:
            raise forms.ValidationError(str(exc))

    # ------------------------------------------------------------------
    # Validação cruzada
    # ------------------------------------------------------------------
    def clean(self):
        cleaned_data = super().clean()

        if self.instance.pk:
            if (
                self.instance.status
                != MaintenanceReservations.Status.AGENDAMENTO
            ):
                raise forms.ValidationError(
                    "Somente manutenções em Agendamento podem ser editadas."
                )
            # Revalida o status sob lock: uma ação em lote pode ter alterado o
            # registro entre a renderização e o POST.
            if connection.in_atomic_block:
                try:
                    locked = (
                        ReservationsRepository.get_maintenance_reservation_for_update(
                            self.instance.pk
                        )
                    )
                except MaintenanceReservations.DoesNotExist:
                    raise forms.ValidationError(
                        "Manutenção não encontrada."
                    )
                if (
                    locked.status
                    != MaintenanceReservations.Status.AGENDAMENTO
                ):
                    raise forms.ValidationError(
                        "Somente manutenções em Agendamento podem ser "
                        f"editadas. Status atual: '{locked.get_status_display()}'."
                    )

        start_date = cleaned_data.get("startDate")
        end_date = cleaned_data.get("endDate")
        if start_date and end_date:
            try:
                validate_maintenance_period(start_date, end_date)
            except MaintenanceReservationValidationError as exc:
                self.add_error("endDate", str(exc))

        return cleaned_data
