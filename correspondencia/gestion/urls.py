from django.contrib.auth import views as auth_views
from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda request: redirect('login')),
    path('portada/', views.portada, name='portada'),
    path('registrar_usuario/', views.crear_usuario, name='registrar_usuario'),
    path('crear_dependencia/', views.crear_dependencia, name='crear_dependencia'),
    path('crear_empresa/', views.registrar_empresa, name='crear_empresa'),
    path('registrar_correspondencia/', views.registro_correspondencia, name='registro_correspondencia'),
    path('index/', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(), name='login'),  # Vista de login de Django
    path('logout/', views.logout_view, name='logout'),
    path('lista_correspondencia/', views.lista_correspondencia, name='lista_correspondencia'),
    path('responder_correspondencia/<int:correspondencia_id>/', views.responder_correspondencia, name='responder_correspondencia'),
]
