from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django import forms
from django.db import models
from domains.gatehouse.models import Shift, ShiftScale, ServiceTransition, UsefulPhoneNumber, Order, VisitorsRegister, Correspondence, Occurrence, Bag, ElectronicTimeClock


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


@admin.register(ServiceTransition)
class ServiceTransitionAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")
    ordering = ["id"]


@admin.register(UsefulPhoneNumber)
class UsefulPhoneNumberAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")


@admin.register(VisitorsRegister)
class VisitorsRegisterAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")


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
