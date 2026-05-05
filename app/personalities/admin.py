from django.contrib import admin
from .models import BusinessSector, Entity

# Register your models here.
@admin.register(BusinessSector)
class BusinessSectorAdmin(admin.ModelAdmin):
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

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'business_sector', 'kind', 'cpf_cnpj')
    search_fields = ('code', 'name', 'cpf_cnpj')
    list_filter = ('business_sector', 'kind')
    ordering = ('business_sector', 'name')
    list_per_page = 25
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'business_sector', 'kind', 'cpf_cnpj', 'rg_ie', 'municipal_registration', 'trade_name', 'date_of_birth_opening', 'sex', 'email', 'phone', 'address', 'observations', 'is_active')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('business_sector', 'name')

