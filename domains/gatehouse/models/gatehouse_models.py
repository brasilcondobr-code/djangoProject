from django.db import models


class Shift(models.Model):
    class Meta:
        app_label = "gatehouse"
        verbose_name = "01. Plantão"
        verbose_name_plural = "01. Plantões"

    collaborator = models.ForeignKey(
        "condominium.Collaborator",
        on_delete=models.CASCADE,
        verbose_name="Colaborador",
    )
    condominium = models.ForeignKey(
        "condominium.Condominium",
        on_delete=models.CASCADE,
        verbose_name="Condomínio",
    )
    startDate = models.DateField(
        verbose_name="Data Inicial",
        help_text="Data inicial do plantão",
    )
    endDate = models.DateField(
        verbose_name="Data Final",
        help_text="Data final do plantão",
    )
    title = models.CharField(
        "Título",
        max_length=255,
        help_text="Título do plantão",
        blank=True,
    )
    status = models.ForeignKey(
        "parameters.AssemblyStatus",
        on_delete=models.CASCADE,
        verbose_name="Status",
        help_text="Status do plantão",
    )
    is_active = models.BooleanField(
        "Ativo",
        default=True,
        help_text="Indica se o plantão está ativo",
    )
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Criado por",
        help_text="Usuário que criou o plantão",
        editable=False,
    )
    created_at = models.DateTimeField(
        "Criado em",
        auto_now_add=True,
        help_text="Data e hora da criação",
    )
    updated_at = models.DateTimeField(
        "Atualizado em",
        auto_now=True,
        help_text="Data e hora da última atualização",
    )

    def __str__(self):
        return "01. Plantão %s" % self.id


class ShiftScale(models.Model):
    class Meta:
        app_label = "gatehouse"
        verbose_name = "01. Escala"
        verbose_name_plural = "01. Escalas"

    def __str__(self):
        return "Escala %s - %s" % (self.description, self.shiftDate)

    shift = models.ForeignKey(
        "gatehouse.Shift",
        on_delete=models.CASCADE,
        verbose_name="Plantão",
        help_text="Plantão ao qual esta escala pertence",
        related_name="scales",
    )
    description = models.CharField(
        "Descrição",
        max_length=255,
        help_text="Descrição da escala",
        blank=True,
    )
    shiftDate = models.DateField(
        "Data da Escala",
        help_text="Data da escala",
    )
    startTime = models.TimeField(
        "Hora Inicial",
        help_text="Hora inicial da escala",
    )
    endTime = models.TimeField(
        "Hora Final",
        help_text="Hora final da escala",
    )
    is_active = models.BooleanField(
        "Ativo",
        default=True,
        help_text="Indica se a escala está ativa",
    )


class ServiceTransition(models.Model):
    class Meta:
        app_label = "gatehouse"
        verbose_name = "02. Passagem de Serviço"
        verbose_name_plural = "02. Passagens de Serviços"

    def __str__(self):
        return "02. Passagem de Serviço"


class UsefulPhoneNumber(models.Model):
    class Meta:
        app_label = "gatehouse"
        verbose_name = "03. Telefone Útil"
        verbose_name_plural = "03. Telefones Úteis"

    def __str__(self):
        return "03. Telefone Útil"


class Order(models.Model):
    class Meta:
        app_label = "gatehouse"
        verbose_name = "04. Encomenda"
        verbose_name_plural = "04. Encomendas"

    def __str__(self):
        return "04. Encomenda"


class VisitorsRegister(models.Model):
    class Meta:
        app_label = "gatehouse"
        verbose_name = "05. Reg. Visitante"
        verbose_name_plural = "05. Reg. Visitantes"

    def __str__(self):
        return "05. Reg. Visitante"


class Correspondence(models.Model):
    class Meta:
        app_label = "gatehouse"
        verbose_name = "06. Correspondência"
        verbose_name_plural = "06. Correspondências"

    def __str__(self):
        return "06. Correspondência"


class Occurrence(models.Model):
    class Meta:
        app_label = "gatehouse"
        verbose_name = "07. Ocorrência"
        verbose_name_plural = "07. Ocorrências"

    def __str__(self):
        return "07. Ocorrência"


class Bag(models.Model):
    class Meta:
        app_label = "gatehouse"
        verbose_name = "08. Malote"
        verbose_name_plural = "08. Malotes"

    def __str__(self):
        return "08. Malote"


class ElectronicTimeClock(models.Model):
    class Meta:
        app_label = "gatehouse"
        verbose_name = "09. Ponto Eletrônico"
        verbose_name_plural = "09. Pontos Eletrônicos"

    def __str__(self):
        return "09. Ponto Eletrônico"
