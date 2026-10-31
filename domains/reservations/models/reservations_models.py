from django.conf import settings
from django.db import models


class Rentals(models.Model):
    """Módulo 01. Locações.

    O período é tratado como intervalo inclusivo: ``startDate`` e ``endDate``
    são datas válidas da locação. A capacidade é controlada por condomínio/
    unidade (:class:`residents.CondominiumUnit`), tipo de locação
    (:class:`parameters.TypesOfRental`) e status.
    """

    class Status(models.TextChoices):
        AGENDAMENTO = "agendamento", "Agendamento"
        RESERVADO = "reservado", "Reservado"
        FINALIZADO = "finalizado", "Finalizado"

    class Meta:
        app_label = 'reservations'
        verbose_name = "01. Locação"
        verbose_name_plural = "01. Locações"
        ordering = ["-startDate", "-id"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(endDate__gte=models.F("startDate")),
                name="rentals_end_date_gte_start_date",
                violation_error_message=(
                    "A data final deve ser maior ou igual à data inicial."
                ),
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "condominium",
                    "typesOfRentals",
                    "status",
                    "is_active",
                ],
                name="rentals_capacity_idx",
            ),
            models.Index(
                fields=["startDate", "endDate"],
                name="rentals_period_idx",
            ),
        ]

    condominium = models.ForeignKey(
        "residents.CondominiumUnit",
        on_delete=models.PROTECT,
        related_name="rentals",
        verbose_name="Unidade",
        help_text="Unidade condominial à qual a locação pertence",
    )
    typesOfRentals = models.ForeignKey(
        "parameters.TypesOfRental",
        on_delete=models.PROTECT,
        related_name="rentals",
        verbose_name="Tipo de locação",
        help_text="Tipo de locação que define os limites de capacidade",
    )
    startDate = models.DateField(
        verbose_name="Data inicial",
        help_text="Data inicial da locação (inclusive)",
    )
    endDate = models.DateField(
        verbose_name="Data final",
        help_text="Data final da locação (inclusive)",
    )
    applicant = models.CharField(
        verbose_name="Solicitante",
        max_length=255,
        help_text="Nome do solicitante da locação",
    )
    rentalPrice = models.DecimalField(
        verbose_name="Valor da locação",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valor cobrado pela locação",
    )
    charge_amount = models.BooleanField(
        verbose_name="Cobrar valor?",
        default=True,
        help_text="Indica se a locação gera cobrança",
    )
    observations = models.TextField(
        verbose_name="Observações",
        blank=True,
        default="",
        help_text="Observações sobre a locação (opcional)",
    )
    is_active = models.BooleanField(
        verbose_name="Ativo",
        default=True,
        help_text="Indica se a locação participa do controle de capacidade",
    )
    status = models.CharField(
        verbose_name="Status",
        max_length=20,
        choices=Status.choices,
        default=Status.AGENDAMENTO,
        editable=False,
        db_index=True,
        help_text="Situação definida pelo servidor",
    )
    errorStatus = models.TextField(
        verbose_name="Erro / motivo da rejeição",
        blank=True,
        default="",
        editable=False,
        help_text="Motivo da última rejeição de operação sobre a locação",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="created_rentals",
        verbose_name="Criado por",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="updated_rentals",
        verbose_name="Atualizado por",
    )
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="Atualizado em",
        auto_now=True,
    )

    def __str__(self):
        identifier = self.applicant or "sem solicitante"
        return f"01. Locação {self.pk or ''} - {identifier}".strip()


class MaintenanceReservations(models.Model):
    """Módulo 02. Manutenções.

    O status é controlado exclusivamente pelo servidor: todo registro nasce
    em ``Agendamento`` e só avança por ações explícitas (Executar/Finalizar).
    """

    class Status(models.TextChoices):
        AGENDAMENTO = "agendamento", "Agendamento"
        EXECUCAO = "execucao", "Execução"
        FINALIZADO = "finalizado", "Finalizado"

    class Meta:
        app_label = 'reservations'
        verbose_name = "02. Manutenção"
        verbose_name_plural = "02. Manutenções"
        ordering = ["-startDate", "-id"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(endDate__gte=models.F("startDate")),
                name="maintenance_reservations_end_date_gte_start_date",
                violation_error_message=(
                    "A data final deve ser maior ou igual à data inicial."
                ),
            ),
        ]

    condominium = models.ForeignKey(
        "residents.CondominiumUnit",
        on_delete=models.PROTECT,
        related_name="maintenance_reservations",
        verbose_name="Unidade",
        help_text="Unidade condominial à qual a manutenção pertence",
    )
    typesOfMaintenance = models.ForeignKey(
        "parameters.TypesOfMaintenanceReservations",
        on_delete=models.PROTECT,
        related_name="maintenance_reservations",
        verbose_name="Tipo de manutenção",
        help_text="Tipo que classifica a manutenção",
    )
    startDate = models.DateField(
        verbose_name="Data inicial",
        help_text="Data inicial da manutenção (inclusive)",
    )
    endDate = models.DateField(
        verbose_name="Data final",
        help_text="Data final da manutenção (inclusive)",
    )
    applicant = models.CharField(
        verbose_name="Solicitante",
        max_length=255,
        help_text="Nome do solicitante da manutenção",
    )
    observations = models.TextField(
        verbose_name="Observações",
        blank=True,
        default="",
        help_text="Observações sobre a manutenção (opcional)",
    )
    is_active = models.BooleanField(
        verbose_name="Ativo",
        default=True,
        help_text="Indica se a manutenção está ativa",
    )
    status = models.CharField(
        verbose_name="Status",
        max_length=20,
        choices=Status.choices,
        default=Status.AGENDAMENTO,
        editable=False,
        db_index=True,
        help_text="Situação definida pelo servidor",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="created_maintenance_reservations",
        verbose_name="Criado por",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="updated_maintenance_reservations",
        verbose_name="Atualizado por",
    )
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="Atualizado em",
        auto_now=True,
    )

    def __str__(self):
        identifier = self.applicant or "sem solicitante"
        prefix = f"02. Manutenção {self.pk}" if self.pk else "02. Manutenção"
        return f"{prefix} - {identifier}"

class MoveReservations(models.Model):
    """Módulo 03. Mudanças.

    O status é controlado exclusivamente pelo servidor: todo registro nasce
    em ``Agendamento`` e só avança por ações explícitas (Executar/Finalizar).
    """

    class TypeOfChange(models.TextChoices):
        ENTRADA = "E", "Entrada"
        SAIDA = "S", "Saída"

    class Status(models.TextChoices):
        AGENDAMENTO = "agendamento", "Agendamento"
        EXECUCAO = "execucao", "Execução"
        FINALIZADO = "finalizado", "Finalizado"

    class Meta:
        app_label = 'reservations'
        verbose_name = "03. Mudança"
        verbose_name_plural = "03. Mudanças"
        ordering = ["-startDate", "-id"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(endDate__gte=models.F("startDate")),
                name="move_reservations_end_date_gte_start_date",
                violation_error_message=(
                    "A data final deve ser maior ou igual à data inicial."
                ),
            ),
        ]

    condominium = models.ForeignKey(
        "residents.CondominiumUnit",
        on_delete=models.PROTECT,
        related_name="move_reservations",
        verbose_name="Unidade",
        help_text="Unidade condominial à qual a mudança pertence",
    )
    typeOfChange = models.CharField(
        verbose_name="Tipo de mudança",
        max_length=1,
        choices=TypeOfChange.choices,
        help_text="Entrada ou saída de bens da unidade",
    )
    startDate = models.DateField(
        verbose_name="Data inicial",
        help_text="Data inicial da mudança (inclusive)",
    )
    endDate = models.DateField(
        verbose_name="Data final",
        help_text="Data final da mudança (inclusive)",
    )
    applicant = models.CharField(
        verbose_name="Solicitante",
        max_length=255,
        help_text="Nome do solicitante da mudança",
    )
    observations = models.TextField(
        verbose_name="Observações",
        blank=True,
        default="",
        help_text="Observações sobre a mudança (opcional)",
    )
    is_active = models.BooleanField(
        verbose_name="Ativo",
        default=True,
        help_text="Indica se a mudança está ativa",
    )
    status = models.CharField(
        verbose_name="Status",
        max_length=20,
        choices=Status.choices,
        default=Status.AGENDAMENTO,
        editable=False,
        db_index=True,
        help_text="Situação definida pelo servidor",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="created_move_reservations",
        verbose_name="Criado por",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="updated_move_reservations",
        verbose_name="Atualizado por",
    )
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="Atualizado em",
        auto_now=True,
    )

    def __str__(self):
        identifier = self.applicant or "sem solicitante"
        prefix = f"03. Mudança {self.pk}" if self.pk else "03. Mudança"
        return f"{prefix} - {identifier}"
