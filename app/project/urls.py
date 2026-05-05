from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from residents.views import get_unit_identification

from .views import home, get_unit_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    ## path('api/unit/<int:unit_id>/', get_unit_data, name='get_unit_data'),
    path('ajax/get-unit-identification/', get_unit_identification, name='get_unit_identification'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
