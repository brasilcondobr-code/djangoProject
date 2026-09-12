import csv

from django.http import HttpResponse
from django.contrib import admin


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)

        writer.writerow([field.verbose_name.title() for field in meta.fields])

        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response

    export_as_csv.short_description = "Exportar para CSV"


class BaseModelAdmin(ExportCsvMixin, admin.ModelAdmin):
    list_per_page = 25
    actions = ["export_as_csv"]
    readonly_fields = ('created_at', 'updated_at')
