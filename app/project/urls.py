from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from domains.residents.views import get_unit_identification

from .views import home, get_unit_data, get_weather_cities, get_weather, get_weather_by_ip, get_condo_indicators

urlpatterns = [
    path('admin/weather-cities/', get_weather_cities, name='get_weather_cities'),
    path('admin/weather/', get_weather, name='get_weather'),
    path('admin/weather-by-ip/', get_weather_by_ip, name='get_weather_by_ip'),
    path('admin/condo-indicators/', get_condo_indicators, name='get_condo_indicators'),
    path('admin/', admin.site.urls),
    path('email/', include('domains.email_service.urls')),
    path('', home, name='home'),
    ## path('api/unit/<int:unit_id/', get_unit_data, name='get_unit_data'),
    path('ajax/get-unit-identification/', get_unit_identification, name='get_unit_identification'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
