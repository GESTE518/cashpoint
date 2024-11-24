
from django.contrib import admin
from django.urls import path, include

from django.conf import settings

from django.conf.urls.static import static

from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
     path('', include('tarif.urls')),
     path('transactions', include('transactions.urls')),
     path('admin/', admin.site.urls),
     path('stock_management/', include('stock_management.urls')),
] 

urlpatterns += i18n_patterns(
    path('', include('tarif.urls')),
)

if settings.DEBUG:

    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)