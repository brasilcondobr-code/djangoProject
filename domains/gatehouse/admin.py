from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django import forms
from django.db import models
from domains.gatehouse.forms import (
    OrderForm,
    ServiceTransitionForm,
    ServiceTransitionObjectForm,
    UsefulPhoneNumberForm,
    VisitorsRegisterForm,
)
from domains.gatehouse.models import (
    Shift, ShiftScale, ServiceTransition,
    ServiceTransitionObject, UsefulPhoneNumber, Order, VisitorsRegister,
    Correspondence, Occurrence, Bag, ElectronicTimeClock,
)


class ShiftScaleInline(admin.TabularInline):
    """Inline para escalas dentro do formulário do plantão."""
    model = ShiftScale
    extra = 1
    fields = ("description", "shiftDate", "startTime", "endTime", "is_active")
    readonly_fields = ("is_active",)
    verbose_name = "Escala"
    verbose_name_plural = "Escalas"
    formfield_overrides = {
        models.TimeField: {
            "widget": forms.TextInput(
                attrs={
                    "class": "vTimeField mask-time",
                    "placeholder": "HH:MM:SS",
                    "maxlength": "8",
                    "size": "10",
                    "autocomplete": "off",
                }
            )
        },
    }


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    """Administração do modelo Shift com abas Principal, Escalas e Auditoria."""

    list_display = (
        "id",
        "collaborator",
        "condominium",
        "startDate",
        "endDate",
        "title",
        "status",
        "is_active",
        "created_at",
    )
    list_filter = ("status", "is_active", "startDate", "endDate", "condominium")
    search_fields = ("title", "collaborator__name", "condominium__name")
    ordering = ["-startDate"]
    filter_horizontal = ()
    jazzmin_section_order = ["Principal", "Escalas", "Auditoria"]

    fieldsets = (
        (
            _("Principal"),
            {
                "fields": (
                    "condominium",
                    "collaborator",
                    "startDate",
                    "endDate",
                    "title",
                    "status",
                ),
            },
        ),
        (
            _("Auditoria"),
            {
                "fields": ("is_active", "created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [ShiftScaleInline]
    readonly_fields = ("created_by", "created_at", "updated_at")

    class Media:
        js = (
            "js/utils.js",
            "js/gatehouse_shift_admin.js",
        )

    def get_queryset(self, request):
        """Otimiza queries com select_related."""
        return super().get_queryset(request).select_related(
            "condominium", "collaborator", "status", "created_by"
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Aplica estilo legível nos selects de Condomínio e Colaborador."""
        if db_field.name in ("collaborator", "condominium"):
            kwargs["widget"] = forms.Select(attrs={
                'style': 'color: #212529 !important; background-color: #ffffff !important; border: 1px solid #ced4da !important;'
            })
            kwargs["queryset"] = db_field.related_model._default_manager.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Preenche o criado_by automaticamente na criação."""
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class ServiceTransitionObjectInline(admin.TabularInline):
    """Inline para objetos vinculados (aba Objetos) dentro da passagem de serviço."""
    model = ServiceTransitionObject
    form = ServiceTransitionObjectForm
    extra = 1
    fields = ("categoryObj", "itemObj", "amountObj", "shiftDate")
    verbose_name = "Objeto"
    verbose_name_plural = "Objetos"


@admin.register(ServiceTransition)
class ServiceTransitionAdmin(admin.ModelAdmin):
    """Administração do modelo ServiceTransition com abas Principal, Objetos e Auditoria."""

    form = ServiceTransitionForm
    list_display = (
        "id",
        "condominium",
        "collaboratorEnd",
        "collaboratorStart",
        "releaseDate",
        "is_active",
        "created_at",
    )
    list_filter = ("condominium", "is_active", "releaseDate")
    search_fields = ("condominium__name", "collaboratorEnd__name", "collaboratorStart__name", "observations")
    ordering = ["-releaseDate", "-id"]
    jazzmin_section_order = ["Principal", "Objetos", "Auditoria"]

    fieldsets = (
        (
            _("Principal"),
            {
                "fields": (
                    "condominium",
                    "collaboratorEnd",
                    "collaboratorStart",
                    "releaseDate",
                    "observations",
                ),
            },
        ),
        (
            _("Auditoria"),
            {
                "fields": ("is_active", "created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [ServiceTransitionObjectInline]
    readonly_fields = ("created_by", "created_at", "updated_at")
    list_per_page = 25

    class Media:
        css = {
            "all": ("gatehouse/css/servicetransition_admin.css",),
        }

    def get_queryset(self, request):
        """Otimiza queries com select_related e prefetch dos objetos."""
        return super().get_queryset(request).select_related(
            "condominium", "collaboratorEnd", "collaboratorStart", "created_by"
        ).prefetch_related("items")

    def save_model(self, request, obj, form, change):
        """Preenche o criado_by automaticamente na criação."""
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(UsefulPhoneNumber)
class UsefulPhoneNumberAdmin(admin.ModelAdmin):
    """Administração do modelo UsefulPhoneNumber com abas Principal e Auditoria.

    Divergência de requisito assumida: o item pede "CRUD completo" mas tambem
    "sem edicao" — aqui a edicao e bloqueada (has_change_permission -> False);
    sao permitidos apenas criar (C), visualizar (R) e excluir (D).
    """

    form = UsefulPhoneNumberForm
    list_display = (
        "id",
        "name",
        "condominium",
        "categoryPhone",
        "phone1",
        "releaseDate",
        "is_active",
    )
    list_filter = ("condominium", "categoryPhone", "is_active")
    search_fields = ("name", "phone1", "condominium__name", "categoryPhone__name")
    ordering = ["name", "id"]
    jazzmin_section_order = ["Principal", "Auditoria"]

    fieldsets = (
        (
            _("Principal"),
            {
                "fields": (
                    "condominium",
                    "categoryPhone",
                    "releaseDate",
                    "name",
                    "phone1",
                    "phone2",
                    "phone3",
                    "phone4",
                    "phone5",
                    "observations",
                ),
            },
        ),
        (
            _("Auditoria"),
            {
                "fields": ("is_active", "created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_by", "created_at", "updated_at")
    list_per_page = 25

    class Media:
        js = (
            "js/utils.js",
            "js/gatehouse_usefulphone_admin.js",
        )

    def get_queryset(self, request):
        """Otimiza queries com select_related."""
        return super().get_queryset(request).select_related(
            "condominium", "categoryPhone", "created_by"
        )

    def save_model(self, request, obj, form, change):
        """Preenche o criado_by automaticamente na criação."""
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        """Bloqueia a edicao (divergencia: 'sem edicao' do modulo 03)."""
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Administração do modelo Order (módulo 04) com abas Principal e Auditoria.

    Edição liberada (decisão de requisito): o CRUD é completo e
    ``created_by`` só é preenchido na criação (nunca sobrescrito na edição).
    """

    form = OrderForm
    list_display = (
        "id",
        "unit",
        "releaseDate",
        "documentNumber",
        "is_active",
    )
    list_filter = ("unit", "is_active")
    search_fields = (
        "documentNumber",
        "observations",
        "unit__unit_number",
        "unit__condominium__name",
    )
    ordering = ["-releaseDate", "-id"]
    jazzmin_section_order = ["Principal", "Auditoria"]

    fieldsets = (
        (
            _("Principal"),
            {
                "fields": (
                    "unit",
                    "releaseDate",
                    "documentNumber",
                    "fileImage",
                    "observations",
                ),
            },
        ),
        (
            _("Auditoria"),
            {
                "fields": ("is_active", "created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_by", "created_at", "updated_at")
    list_per_page = 25

    class Media:
        js = ("js/gatehouse_order_admin.js",)

    def get_queryset(self, request):
        """Otimiza queries com select_related."""
        return super().get_queryset(request).select_related(
            "unit", "unit__condominium", "created_by"
        )

    def save_model(self, request, obj, form, change):
        """Preenche created_by apenas na criação (nunca sobrescrito)."""
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """Após salvar o pedido, persiste as fotos do botão 'Foto'."""
        super().save_related(request, form, formsets, change)
        form.persist_photos(form.instance, request.user)


@admin.register(VisitorsRegister)
class VisitorsRegisterAdmin(admin.ModelAdmin):
    """Administração do modelo VisitorsRegister (módulo 05) com abas.

    Edição liberada (decisão de requisito). Divergência aprovada: aqui
    ``created_by`` passa a representar o usuário da última gravação
    (criação e edição) — os demais módulos preservam o criador original.
    """

    form = VisitorsRegisterForm
    list_display = (
        "id",
        "visitor",
        "visitDate",
        "is_active",
        "created_at",
    )
    list_filter = ("visitor", "is_active", "visitDate")
    search_fields = ("visitor__name", "observations")
    ordering = ["-visitDate", "-id"]
    jazzmin_section_order = ["Principal", "Auditoria"]

    fieldsets = (
        (
            _("Principal"),
            {
                "fields": ("visitor", "visitDate", "observations"),
            },
        ),
        (
            _("Auditoria"),
            {
                "fields": ("is_active", "created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_by", "created_at", "updated_at")
    list_per_page = 25

    def get_queryset(self, request):
        """Otimiza queries com select_related."""
        return super().get_queryset(request).select_related(
            "visitor", "created_by"
        )

    def save_model(self, request, obj, form, change):
        """created_by = usuário desta gravação (criação e edição)."""
        obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Correspondence)
class CorrespondenceAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")


@admin.register(Occurrence)
class OccurrenceAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")


@admin.register(Bag)
class BagAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")


@admin.register(ElectronicTimeClock)
class ElectronicTimeClockAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")
