from django.contrib import admin

from domains.condominium.models import Condominium, Collaborator, TypesCollaborator
from domains.condominium.services import CondominiumService, CollaboratorService
from shared.admin import BaseModelAdmin


@admin.register(Condominium)
class CondominiumAdmin(BaseModelAdmin):
    list_display = ('code', 'name', 'cnpj', 'state_registration', 'municipal_registration', 'type_condominium', 'address', 'is_active')
    search_fields = ('name', 'code', 'cnpj')
    list_filter = ('code', 'is_active')

    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'js/utils.js',
            'js/custom-condominium-condominium.js',
        )


@admin.register(TypesCollaborator)
class TypesCollaboratorsAdmin(BaseModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)


@admin.register(Collaborator)
class CollaboratorsAdmin(BaseModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'type_collaborator', 'condominium', 'photo', 'is_active')
    search_fields = ('condominium__name', 'name', 'email')
    list_filter = ('condominium', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'api_status', 'retorno_api', 'date_time_appointment')

    fieldsets = (
        (None, {
            'fields': (
                'condominium',
                'name',
                'cpf',
                'rg',
                'email',
                'phone_number',
                'type_collaborator',
                'is_active',
                'photo',
                'observations',
            )
        }),
        ('Receita Federal', {
            'fields': ('situation', 'regular', 'death', 'api_status', 'retorno_api', 'date_time_appointment'),
        }),
        ('Antecedentes', {
            'fields': ('certificate_presentation_date', 'certificate_validity', 'observations_certificate', 'certificate_file'),
        }),
    )

    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'js/utils.js',
            'js/custom-condominium-collaborators.js',
        )
