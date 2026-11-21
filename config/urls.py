from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.portal.urls', namespace='portal')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('academics/', include('apps.academics.urls', namespace='academics')),
    path('assessments/', include('apps.assessments.urls', namespace='assessments')),
    path('results/', include('apps.results.urls', namespace='results')),
    path('finance/', include('apps.finance.urls', namespace='finance')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
