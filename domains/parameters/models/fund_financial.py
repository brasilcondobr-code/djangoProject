from django.db import models


class FundFinancial(models.Model):
    class Meta:
        app_label = 'parameters'
        verbose_name = '29. Fundo'
        verbose_name_plural = '29. Fundos'
        ordering = ['description']
        db_table = 'parameters_fundfinancial'
        constraints = [
            models.UniqueConstraint(
                fields=['condominium', 'description'],
                name='uq_fundfinancial_condominium_description',
                violation_error_message=(
                    'Já existe um fundo com esta descrição para o '
                    'condomínio selecionado.'
                ),
            ),
        ]

    condominium = models.ForeignKey(
        'condominium.Condominium',
        on_delete=models.CASCADE,
        related_name='fund_financials',
        null=False,
        blank=False,
        verbose_name='Condomínio',
        help_text='Condomínio ao qual o fundo pertence',
    )

    description = models.CharField(
        verbose_name='Descrição',
        max_length=255,
        null=False,
        blank=False,
    )

    is_active = models.BooleanField(
        verbose_name='Ativo',
        default=True,
    )

    created_at = models.DateTimeField(
        verbose_name='Criado em',
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name='Atualizado em',
        auto_now=True,
    )

    def __str__(self):
        return self.description
