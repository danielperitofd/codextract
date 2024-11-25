# fileprocessor/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('processar/', views.processar_arquivos, name='processar_arquivos'),  # Página de processamento
    path('home/', views.home, name='home'),  # Agora temos o '/home'
    path('extraidos/', views.arquivos_extraidos, name='arquivos_extraidos'),  # A URL para arquivos extraídos
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
