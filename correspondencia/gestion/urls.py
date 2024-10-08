from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda request: redirect('login')),
    path('portada/', views.portada, name='portada'),
    path('registrar_usuario/', views.registrar_usuario, name='registrar_usuario'),
    path('crear_dependencia/', views.crear_dependencia, name='crear_dependencia'),
    path('crear_empresa/', views.registrar_empresa, name='crear_empresa'),
    path('registro_correspondencia/<int:empresa_id>/', views.registro_correspondencia, name='registro_correspondencia'),
    path('index/', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(), name='login'),  # Vista de login de Django
    path('logout/', views.logout_view, name='logout'),
    path('lista_correspondencia/', views.lista_correspondencia, name='lista_correspondencia'),
    path('responder_correspondencia/<int:correspondencia_id>/', views.responder_correspondencia, name='responder_correspondencia'),
    path('adjuntar_documento/<int:correspondencia_id>/', views.adjuntar_documento, name='adjuntar_documento'),
    path('ver_respuesta/<int:correspondencia_id>/', views.ver_respuesta, name='ver_respuesta'),
    path('exportar_excel/', views.exportar_excel, name='exportar_excel'),
    path('filtrar_dependencias/', views.filtrar_dependencias_por_empresa, name='filtrar_dependencias_por_empresa'),
    path('editar_empresa/<int:empresa_id>/', views.editar_empresa, name='editar_empresa'),
    path('editar_dependencia/<int:dependencia_id>/', views.editar_dependencia, name='editar_dependencia'),
    path('editar_usuario/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('error/', views.error_view, name='error'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 