from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    #path('osi/file/', include('ncProjects.apps.file_osi.urls')),
    #path('osi/fields/', include('ncProjects.apps.fields_osi.urls')),
    #path('', include('ncProjects.apps.PCOS_app.urls')),
    path('',include('Starts.urls')),
    path('',include('Pcos.urls')),
    path('',include('Osi.urls')),
    path('',include('fdb_integration.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
