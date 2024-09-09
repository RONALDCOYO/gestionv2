from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('crear-dependencia/', views.crear_dependencia, name='crear_dependencia'),
]
