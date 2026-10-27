from django.contrib import admin

from .forms import BusinessSectorForm, EntityForm
from domains.personalities.models.entity import Entity
from domains.personalities.models.business_sector import BusinessSector

# Register your models here.
@admin.register(BusinessSector)
class BusinessSectorAdmin(admin.ModelAdmin):
    form = BusinessSectorForm
    list_display = ('description', 'is_active')
    search_fields = ('description',)
    list_filter = ('description', 'is_active')
    ordering = ('description',)
    list_per_page = 25
    fieldsets = (
        (None, {
            'fields': ('description', 'is_active')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    class Meta:
        verbose_name = "1. Ramo de Atividade"
        verbose_name_plural = "1. Ramos de Atividade"
        ordering = ["description"]
        unique_together = ['description']
        db_table = 'personalities_businesssector'
        
    class Media:
        js = (
            'js/utils.js',
        )


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    form = EntityForm
    list_display = ('code', 'kind', 'business_sector', 'name', 'cpf_cnpj', 'is_active')
    list_display_links = ('code', 'name')
    search_fields = ('code', 'name', 'cpf_cnpj')
    list_filter = ('kind', 'is_active', 'business_sector')
    ordering = ('name',)
    list_per_page = 25
    
    fieldsets = (
        (None, {
            'fields': (
                'code', 'kind', 'business_sector', 'name', 'trade_name', 
                'cpf_cnpj', 'rg_ie', 'municipal_registration', 
                'date_of_birth_opening', 'sex', 'email', 'phone', 
                'address', 'observations', 'is_active'
            )
        }),
        ('Receita Federal', {
            'fields': ('situation', 'regular', 'death', 'api_status', 'retorno_api', 'date_time_appointment'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'api_status', 'retorno_api', 'date_time_appointment')

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('business_sector', 'name')

    class Meta:
        verbose_name = "2. Entidade"
        verbose_name_plural = "2. Entidades"
        ordering = ["business_sector", "name", "cpf_cnpj"]
        unique_together = ['business_sector', 'cpf_cnpj']
        db_table = 'personalities_entity'
        
    class Media:
        js = (
            'js/utils.js',
        )