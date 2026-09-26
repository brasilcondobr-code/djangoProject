from django.contrib import admin
from django.db import IntegrityError, transaction

from .models import (
    Addresses, States, TypesCondominium, StructionCondominium,
    TypesVisitorRestrictions, ResidentType, DocumentType, InfractionsType,
    MeterType, AssetType, AssetCategory, AssetStatus, AssetStateCondition,
    AssetBrand, AssetMaintenanceFrequency, BankAccountType,
    Chartofaccountstype, Accountingclasstypes, ChartofaccountsMaingroup,
    ChartofaccountsSubgroup, ChartofaccountsStatus, VotingType,
    AssemblyStatus, TopicOption, ConciergeServiceCategory,
)
from .forms import AddressesForm, StatesForm, TypesVisitorRestrictionsForm, ResidentTypeForm, DocumentTypeForm, InfractionsTypeForm, VotingTypeForm, AssemblyStatusForm, TopicOptionForm, ConciergeServiceCategoryForm


@admin.register(TypesCondominium)
class TypesCondominiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    class Meta:
        verbose_name = "1. Tipo de Condomínio"
        verbose_name_plural = "1. Tipos de Condomínios"
        ordering = ["name", "is_active", "created_at"]
        unique_together = ['name']
        db_table = 'condominium_typescondominium'


@admin.register(StructionCondominium)
class StructionCondominiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    class Meta:
        verbose_name = "2. Estrutura do Condomínio"
        verbose_name_plural = "2. Estruturas dos Condomínios"
        ordering = ["name", "is_active", "created_at"]
        unique_together = ['name']
        db_table = 'condominium_structioncondominium'


@admin.register(States)
class StatesAdmin(admin.ModelAdmin):
    form = StatesForm
    list_display = ('name', 'abbreviation', 'capital', 'region')
    search_fields = ('name', 'abbreviation', 'capital', 'region')
    list_filter = ('name', 'abbreviation')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    class Meta:
        verbose_name = "3. Estado"
        verbose_name_plural = "3. Estados"
        ordering = ["abbreviation", "name", "region"]
        unique_together = ['name', 'abbreviation']
        db_table = 'condominium_states'
        
    class Media:
        js = (
            'js/custom-parameters-states.js',
            )


@admin.register(Addresses)
class AddressesAdmin(admin.ModelAdmin):
    form = AddressesForm
    list_display = ('street', 'number', 'neighborhood', 'city', 'state', 'is_active')
    search_fields = ('street', 'city', 'state')
    list_filter = ('state', 'city', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    class Meta:
        verbose_name = "4. Endereço"
        verbose_name_plural = "4. Endereços"
        ordering = ["street", "number", "city", "state", "is_active", "created_at"]
        unique_together = ['street', 'number', 'neighborhood', 'city', 'state', 'zip_code']
        
    class Media:
        js = (
            'js/custom-parameters-address.js',
            )


@admin.register(TypesVisitorRestrictions)
class TypesVisitorRestrictionsAdmin(admin.ModelAdmin):
    form = TypesVisitorRestrictionsForm
    list_display = ('description', 'is_active')
    search_fields = ('description',)
    list_filter = ('is_active',)
    ordering = ('description',)
    list_per_page = 25
    fieldsets = (
        (None, {
            'fields': ('description', 'is_active')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    class Meta:
        verbose_name = "5. Tipo de Restrição para Visitante"
        verbose_name_plural = "5. Tipos de Restrição para Visitantes"
        ordering = ["description"]
        unique_together = ['description']
        db_table = 'personalities_typesvisitorrestrictions'
        
    class Media:
        js = (
            'js/custom-parameters-types-visitor-restrictions.js',
            )


@admin.register(ResidentType)
class ResidentTypeAdmin(admin.ModelAdmin):
    form = ResidentTypeForm
    list_display = ('description', 'is_active')
    search_fields = ('description',)
    list_filter = ('is_active',)
    ordering = ('description',)
    list_per_page = 25


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    form = DocumentTypeForm
    list_display = ('description', 'is_active')
    search_fields = ('description',)
    list_filter = ('is_active',)
    ordering = ('description',)
    list_per_page = 25


@admin.register(InfractionsType)
class InfractionsTypeAdmin(admin.ModelAdmin):
    form = InfractionsTypeForm
    list_display = ('description', 'infraction_type', 'is_active')
    search_fields = ('description',)
    list_filter = ('infraction_type', 'is_active',)
    ordering = ('description',)
    list_per_page = 25


@admin.register(MeterType)
class MeterTypeAdmin(admin.ModelAdmin):
    list_display = ('description', 'is_active')
    search_fields = ('description',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ('description', 'is_active')
    search_fields = ('description',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ('description', 'is_active')
    search_fields = ('description',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(AssetStatus)
class AssetStatusAdmin(admin.ModelAdmin):
    list_display = ('description', 'is_active')
    search_fields = ('description',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(AssetStateCondition)
class AssetStateConditionAdmin(admin.ModelAdmin):
    list_display = ('description', 'is_active')
    search_fields = ('description',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(AssetBrand)
class AssetBrandAdmin(admin.ModelAdmin):
    list_display = ('description', 'is_active')
    search_fields = ('description',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(AssetMaintenanceFrequency)
class AssetMaintenanceFrequencyAdmin(admin.ModelAdmin):
    list_display = ('description', 'is_active')
    search_fields = ('description',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(BankAccountType)
class BankAccountTypeAdmin(admin.ModelAdmin):
    list_display = ('description', 'is_active')
    search_fields = ('description',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(Chartofaccountstype)
class ChartofaccountstypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'nature', 'is_active')
    search_fields = ('code', 'description')
    list_filter = ('nature', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(Accountingclasstypes)
class AccountingclasstypesAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'account_type', 'is_active')
    search_fields = ('code', 'description', 'account_type__description')
    list_filter = ('account_type', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(ChartofaccountsMaingroup)
class ChartofaccountsMaingroupAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'account_class', 'is_active')
    search_fields = ('code', 'description', 'account_class__description')
    list_filter = ('account_class', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(ChartofaccountsSubgroup)
class ChartofaccountsSubgroupAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'main_group', 'is_active')
    search_fields = ('code', 'description', 'main_group__description')
    list_filter = ('main_group', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(ChartofaccountsStatus)
class ChartofaccountsStatusAdmin(admin.ModelAdmin):
    list_display = ('description', 'is_active')
    search_fields = ('description',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(VotingType)
class VotingTypeAdmin(admin.ModelAdmin):
    form = VotingTypeForm
    list_display = ('description', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('description',)
    search_fields = ('description',)
    list_filter = ('is_active',)
    ordering = ('description',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    empty_value_display = '-'
    
    fieldsets = (
        ('Dados principais', {
            'fields': ('description', 'is_active'),
        }),
        ('Auditoria', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(AssemblyStatus)
class AssemblyStatusAdmin(admin.ModelAdmin):
    form = AssemblyStatusForm
    list_display = (
        'description', 'is_pending', 'is_running', 'is_complete',
        'is_active', 'created_at', 'updated_at',
    )
    list_display_links = ('description',)
    search_fields = ('description',)
    list_filter = ('is_pending', 'is_running', 'is_complete', 'is_active')
    ordering = ('description',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    empty_value_display = '-'


@admin.register(TopicOption)
class TopicOptionAdmin(admin.ModelAdmin):
    form = TopicOptionForm
    list_display = ('description', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('description',)
    search_fields = ('description',)
    list_filter = ('is_active',)
    ordering = ('description',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    empty_value_display = '-'

@admin.register(ConciergeServiceCategory)
class ConciergeServiceCategoryAdmin(admin.ModelAdmin):
    form = ConciergeServiceCategoryForm
    list_display = ('description', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('description',)
    search_fields = ('description',)
    list_filter = ('is_active',)
    ordering = ('description',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    empty_value_display = '-'

    fieldsets = (
        ('Dados principais', {
            'fields': ('description', 'is_active'),
        }),
        ('Auditoria', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )
