from django.contrib import admin


class BaseModelAdmin(admin.ModelAdmin):
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')
