from django.conf import settings
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
    class Meta:
        app_label = 'financial'
        verbose_name = "04. Cobrança"
        verbose_name_plural = "04. Cobranças"

    def __str__(self):
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
                    | models.Q(launchType="D", value__lt=0)
                    | models.Q(launchType="C", value__gt=0)
                ),
                name="ck_newrelease_value_sign_matches_launch_type",
                violation_error_message=(
                    "O valor deve ser negativo para débito e positivo para "
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
            "negativo e crédito como positivo."
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
    class Meta:
        app_label = 'financial'
        verbose_name = "08. Pagamento"
        verbose_name_plural = "08. Pagamentos"

    def __str__(self):
        return "08. Pagamento"

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
