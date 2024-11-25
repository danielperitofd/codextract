
from django.contrib import admin
from django.urls import path, include
from fileprocessor import views  # Importando a view para a rota inicial
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='home'),  # Rota para a página inicial
    path('admin/', admin.site.urls),
    path('fileprocessor/', include('fileprocessor.urls')),
    path('', include('fileprocessor.urls')),  # Adiciona as URLs do fileprocessor

]

# Serve arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    