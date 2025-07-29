from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from fdb_integration.views import proxy_view

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('osi/file/', include('ncProjects.apps.file_osi.urls')),
    #path('osi/fields/', include('ncProjects.apps.fields_osi.urls')),
    #path('', include('ncProjects.apps.PCOS_app.urls')),
    path('',include('Starts.urls')),
    path('',include('Pcos.urls')),
    path('',include('Osi.urls')),
    path('',include('fdb_integration.urls')),

    # Прокси-маршруты для FastAPI сервисов
    re_path(r'^api/auth/(?P<path>.*)$', proxy_view, {'service_url': 'http://localhost:8000'}),
    re_path(r'^api/storage/(?P<path>.*)$', proxy_view, {'service_url': 'http://localhost:8001'}),
    re_path(r'^api/data/(?P<path>.*)$', proxy_view, {'service_url': 'http://localhost:8002'}),
    re_path(r'^api/visualization/(?P<path>.*)$', proxy_view, {'service_url': 'http://localhost:8003'}),
    re_path(r'^api/missing/(?P<path>.*)$', proxy_view, {'service_url': 'http://localhost:8004'}),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
