from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

class Agreement(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "01. Acordo"
        verbose_name_plural = "01. Acordos"

    def __str__(self):
        return "01. Acordo"

class PaymentSlip(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "02. Boleto"
        verbose_name_plural = "02. Boletos"

    def __str__(self):
        return "02. Boleto"

class Cash(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "03. Caixa"
        verbose_name_plural = "03. Caixa"

    def __str__(self):
        return "03. Caixa"

class Collection(models.Model):
    """04. Cobranças.

    O status, a data de cobrança, o saldo e os valores calculados são
    controlados exclusivamente pelo servidor (``CollectionService``).
    """

    class Status(models.TextChoices):
        TO_BE_WON = "to_be_won", "A vencer"
        EXPIRED = "expired", "Vencido"
        PAID = "paid", "Pago"
        PARTIAL = "partial", "Parcial"

    class Meta:
        app_label = 'financial'
        verbose_name = "04. Cobrança"
        verbose_name_plural = "04. Cobranças"
        ordering = ["-billingDate", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["condominium", "billingDate", "scope", "dueDate"],
                name="uq_collection_unit_billing_scope_due",
                violation_error_message=(
                    "Já existe uma cobrança para esta unidade, data de "
                    "cobrança, competência e vencimento."
                ),
            ),
        ]

    PERCENT_VALIDATORS = [
        MinValueValidator(Decimal("0.00")),
        MaxValueValidator(Decimal("100.00")),
    ]

    condominium = models.ForeignKey(
        "residents.CondominiumUnit",
        on_delete=models.PROTECT,
        related_name="collections",
        verbose_name="Condomínio/Unidade",
        help_text="Unidade condominial à qual a cobrança pertence.",
    )
    billingDate = models.DateField(
        verbose_name="Data da cobrança",
        help_text="Preenchida automaticamente com a data atual na inclusão.",
    )
    scope = models.DateField(
        verbose_name="Competência",
        help_text="Competência normalizada para o primeiro dia do mês.",
    )
    originalValue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor original",
    )
    discountPercent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=PERCENT_VALIDATORS,
        verbose_name="% Desconto",
    )
    discountAmount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Valor do desconto",
    )
    penaltyPercent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=PERCENT_VALIDATORS,
        verbose_name="% Multa",
    )
    fineAmount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Valor da multa",
    )
    feesPercent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=PERCENT_VALIDATORS,
        verbose_name="% Juros",
    )
    interestAmount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Valor dos juros",
    )
    chargesPercent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=PERCENT_VALIDATORS,
        verbose_name="% Encargos",
    )
    chargesAmount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Valor dos encargos",
    )
    discountDeadline = models.DateField(
        verbose_name="Data limite para desconto",
    )
    dueDate = models.DateField(
        verbose_name="Data de vencimento",
    )
    totalAmount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Valor total",
    )
    balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        verbose_name="Saldo",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TO_BE_WON,
        editable=False,
        db_index=True,
        verbose_name="Status",
    )
    errorStatus = models.TextField(
        blank=True,
        default="",
        editable=False,
        verbose_name="Erro de status",
        help_text="Último motivo de rejeição registrado pelo servidor.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_collections",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Criado por",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="updated_collections",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Atualizado por",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )

    def save(self, *args, **kwargs):
        if self.scope:
            self.scope = self.scope.replace(day=1)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.pk:
            unit = self.condominium
            return f"Cobrança #{self.pk} - {unit} - {self.scope:%m/%Y}"
        return "04. Cobrança"

class Shopping(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "05. Compra"
        verbose_name_plural = "05. Compras"

    def __str__(self):
        return "05. Compra"

class Loan(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "06. Empréstimo"
        verbose_name_plural = "06. Empréstimos"

    def __str__(self):
        return "06. Empréstimo"

class NewRelease(models.Model):
    """07. Lançamentos financeiros.

    O status é controlado exclusivamente pelo servidor: todo registro nasce
    em ``Lançamento`` e só avança para ``Cobrança`` por ação explícita.
    """

    class LaunchType(models.TextChoices):
        DEBITO = "D", "Débito"
        CREDITO = "C", "Crédito"

    class Status(models.TextChoices):
        LANCAMENTO = "lancamento", "Lançamento"
        COBRANCA = "cobranca", "Cobrança"

    class Meta:
        app_label = 'financial'
        verbose_name = "07. Lançamento"
        verbose_name_plural = "07. Lançamentos"
        ordering = ["-launchDate", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "condominium",
                    "title",
                    "scope",
                    "launchDate",
                ],
                name="uq_newrelease_condominium_title_scope_launchdate",
                violation_error_message=(
                    "Já existe um lançamento com este título, competência e "
                    "data para a unidade selecionada."
                ),
            ),
            models.CheckConstraint(
                check=(
                    models.Q(value__isnull=True)
                    | models.Q(launchType="D", value__gt=0)
                    | models.Q(launchType="C", value__lt=0)
                ),
                name="ck_newrelease_value_sign_matches_launch_type",
                violation_error_message=(
                    "O valor deve ser positivo para débito e negativo para "
                    "crédito."
                ),
            ),
        ]

    condominium = models.ForeignKey(
        "residents.CondominiumUnit",
        on_delete=models.PROTECT,
        related_name="new_releases",
        verbose_name="Condomínio/Unidade",
        help_text="Unidade condominial à qual o lançamento pertence.",
    )
    paymaster = models.ForeignKey(
        "residents.Resident",
        on_delete=models.PROTECT,
        related_name="new_releases_as_paymaster",
        verbose_name="Pagador",
        help_text="Morador responsável pelo lançamento.",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Título",
    )
    scope = models.DateField(
        verbose_name="Competência",
        help_text="Selecione o mês e o ano da competência.",
    )
    launchDate = models.DateField(
        verbose_name="Data do lançamento",
    )
    chartOfAccounts = models.ForeignKey(
        "administrative.ChartOfAccount",
        on_delete=models.PROTECT,
        related_name="new_releases",
        verbose_name="Plano de contas",
        help_text="Plano de contas do condomínio da unidade.",
    )
    fund = models.ForeignKey(
        "parameters.FundFinancial",
        on_delete=models.PROTECT,
        related_name="new_releases",
        verbose_name="Fundo",
        help_text="Fundo do condomínio da unidade.",
    )
    collection = models.ForeignKey(
        "financial.Collection",
        on_delete=models.PROTECT,
        related_name="new_releases",
        null=True,
        blank=True,
        verbose_name="Cobrança",
        help_text="Cobrança à qual o lançamento está vinculado.",
    )
    launchType = models.CharField(
        max_length=1,
        choices=LaunchType.choices,
        default=LaunchType.DEBITO,
        verbose_name="Tipo de lançamento",
    )
    value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor",
        help_text=(
            "Informe o valor sem o símbolo R$. Débito é armazenado como "
            "positivo e crédito como negativo."
        ),
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Observações",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.LANCAMENTO,
        editable=False,
        db_index=True,
        verbose_name="Status",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_new_releases",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Criado por",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="updated_new_releases",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Atualizado por",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )

    def save(self, *args, **kwargs):
        if self.scope:
            self.scope = self.scope.replace(day=1)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.scope:
            return f"{self.title} - {self.scope:%m/%Y}"
        return self.title or "07. Lançamento"

class Payment(models.Model):
    """08. Pagamentos recebidos de uma cobrança."""

    class Meta:
        app_label = 'financial'
        verbose_name = "08. Pagamento"
        verbose_name_plural = "08. Pagamentos"
        ordering = ["-dateReceived", "-id"]

    collection = models.ForeignKey(
        "financial.Collection",
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="Cobrança",
    )
    financialTransaction = models.ForeignKey(
        "parameters.FinancialTransaction",
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="Operação financeira",
    )
    dateReceived = models.DateField(
        verbose_name="Data de recebimento",
    )
    amountReceived = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Valor recebido",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_payments",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Criado por",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="updated_payments",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Atualizado por",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )

    def __str__(self):
        if self.pk:
            return f"Pagamento #{self.pk} - Cobrança #{self.collection_id}"
        return "08. Pagamento"


class CollectionCredit(models.Model):
    """Crédito aplicado a uma cobrança, distinto de um pagamento."""

    class Meta:
        app_label = 'financial'
        verbose_name = "Crédito de cobrança"
        verbose_name_plural = "Créditos de cobrança"
        ordering = ["-creditDate", "-id"]

    collection = models.ForeignKey(
        "financial.Collection",
        on_delete=models.PROTECT,
        related_name="credits",
        verbose_name="Cobrança",
    )
    financialTransaction = models.ForeignKey(
        "parameters.FinancialTransaction",
        on_delete=models.PROTECT,
        related_name="collection_credits",
        verbose_name="Operação financeira",
    )
    creditDate = models.DateField(
        verbose_name="Data do crédito",
    )
    amountCredit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Valor do crédito",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_collection_credits",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Criado por",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="updated_collection_credits",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Atualizado por",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )

    def __str__(self):
        if self.pk:
            return f"Crédito #{self.pk} - Cobrança #{self.collection_id}"
        return "Crédito de cobrança"

class Apportionment(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "09. Rateio"
        verbose_name_plural = "09. Rateios"

    def __str__(self):
        return "09. Rateio"

class Receipt(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "10. Recebimento"
        verbose_name_plural = "10. Recebimentos"

    def __str__(self):
        return "10. Recebimento"

class BankTransfer(models.Model):
    class Meta:
        app_label = 'financial'
        verbose_name = "11. Remessa Bancária"
        verbose_name_plural = "11. Remessas Bancárias"

    def __str__(self):
        return "11. Remessa Bancária"
