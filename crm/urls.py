from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static




admin.site.site_header = 'CRM'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clients.urls')),
    path('ai/', include('ai.urls')),
    path('customers/', include('customers.urls')),
    path('business/', include('business.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)